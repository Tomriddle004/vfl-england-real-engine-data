#!/usr/bin/env python3
"""
VFL England History Scraper v5 — Capture Full WS Auth Sequence
==============================================================
Strategy:
1. Login to SportyBet, navigate to virtual page
2. Use CDP to capture ALL WS frames sent by the page (the full auth sequence)
3. Replay the EXACT same auth sequence on our own websockets connection
4. Then send /eventBlocks/find requests on our own connection

The key difference from v2: we capture the FULL login sequence including
any tokens/cookies that the page sends, not just the clientId.
"""
import asyncio
import json
import re
import csv
import os
import time
from datetime import datetime, timezone
from playwright.async_api import async_playwright
import websockets

# Config
OUTPUT_CSV = "/home/ubuntu/vfl_scraper/england_real_scores.csv"
STATE_FILE = "/home/ubuntu/vfl_scraper/real_scores_state.json"
LOG_FILE = "/home/ubuntu/vfl_scraper/real_scores.log"
TARGET_LEAGUE = 7838
CONTENT_ID = 41104
CALC_ID = 515589

CSV_HEADER = [
    "champ_id", "match_day", "date", "home_team", "away_team",
    "ft_home", "ft_away", "ht_home", "ht_away",
    "result", "total_goals", "gg", "odd_values"
]


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def extract_score_from_won_markets(won_markets):
    for m in won_markets:
        match = re.match(r'^_(\d+)_(\d+)$', m)
        if match:
            return int(match.group(1)), int(match.group(2))
    return None, None


def extract_ht_score(won_markets, half_won_markets):
    for m in won_markets:
        match = re.match(r'^HT_(\d+)_(\d+)$', m)
        if match:
            return int(match.group(1)), int(match.group(2))
    if half_won_markets:
        for m in half_won_markets:
            match = re.match(r'^_(\d+)_(\d+)$', m)
            if match:
                return int(match.group(1)), int(match.group(2))
    return None, None


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"cursor_time": None, "total_matches": 0, "page": 0, "min_league": 999999}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


async def capture_auth_sequence():
    """
    Login to SportyBet, navigate to virtual page, and capture the full
    WS authentication sequence that the page sends.
    Returns: (client_id, auth_frames_sent, auth_frames_received)
    """
    log("Launching browser to capture WS auth sequence...")
    
    auth_frames_sent = []
    auth_frames_received = []
    client_id = None
    ws_url = None
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"
        )
        page = await context.new_page()
        
        # CDP to capture all WS frames
        cdp = await context.new_cdp_session(page)
        await cdp.send("Network.enable")
        
        def on_ws_created(params):
            nonlocal ws_url
            url = params.get("url", "")
            if "virtustec" in url:
                ws_url = url
                log(f"WS URL: {url}")
        
        def on_frame_sent(params):
            nonlocal client_id
            payload = params.get("response", {}).get("payloadData", "")
            if payload:
                auth_frames_sent.append(payload)
                if "clientId" in payload:
                    try:
                        d = json.loads(payload)
                        cid = d.get("req", {}).get("headers", {}).get("clientId")
                        if cid:
                            client_id = cid
                    except:
                        pass
        
        def on_frame_received(params):
            payload = params.get("response", {}).get("payloadData", "")
            if payload:
                auth_frames_received.append(payload)
        
        cdp.on("Network.webSocketCreated", on_ws_created)
        cdp.on("Network.webSocketFrameSent", on_frame_sent)
        cdp.on("Network.webSocketFrameReceived", on_frame_received)
        
        # Login
        log("Logging in to SportyBet...")
        await page.goto("https://www.sportybet.com/ng/m/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        for sel in ["text=LATER", "text=Later", "text=Cancel", "text=Not Now", "text=OK"]:
            try:
                await page.click(sel, timeout=2000)
                break
            except:
                pass
        
        for sel in ["text=Log in", "text=Login", "text=LOG IN"]:
            try:
                await page.click(sel, timeout=3000)
                await asyncio.sleep(2)
                break
            except:
                pass
        
        inputs = await page.query_selector_all("input")
        for inp in inputs:
            itype = await inp.get_attribute("type") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            if itype == "tel" or "phone" in placeholder.lower():
                await inp.fill("08139178920")
            elif itype == "password":
                await inp.fill("yahooZE0147!")
        await asyncio.sleep(1)
        
        for sel in ["button:has-text('Login')", "button:has-text('Log In')", "button[type='submit']"]:
            try:
                await page.click(sel, timeout=3000)
                break
            except:
                pass
        await asyncio.sleep(5)
        log("Login done")
        
        # Navigate to virtual page
        await page.goto("https://www.sportybet.com/ng/m/virtual?v4=true", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(10)
        
        # Click England
        for f in page.frames:
            if "virtustec" in f.url:
                try:
                    await f.click("text=England", timeout=10000)
                    await asyncio.sleep(8)
                except:
                    pass
                break
        
        # Wait a bit more for all auth frames to be exchanged
        await asyncio.sleep(5)
        
        await browser.close()
    
    log(f"Captured: {len(auth_frames_sent)} sent frames, {len(auth_frames_received)} received frames")
    log(f"clientId: {client_id}")
    log(f"WS URL: {ws_url}")
    
    return client_id, ws_url, auth_frames_sent, auth_frames_received


async def scrape_with_replayed_auth(client_id, ws_url, auth_frames_sent):
    """
    Open our own WS connection and replay the auth sequence,
    then scrape history data.
    """
    state = load_state()
    
    if not os.path.exists(OUTPUT_CSV) or state["total_matches"] == 0:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
        state["total_matches"] = 0
        state["page"] = 0
        state["min_league"] = 999999
    
    cursor_time = state.get("cursor_time")
    if cursor_time is None:
        cursor_time = int(time.time())
    
    page_num = state["page"]
    
    log(f"Connecting to WS: {ws_url}")
    
    try:
        async with websockets.connect(ws_url, max_size=50_000_000) as ws:
            # Replay only essential auth frames (loginHwId, sync, playlists)
            # Skip tickets and other non-essential frames that return 401
            essential_resources = ["/session/loginHwId", "/session/sync", "/playlists/"]
            log(f"Replaying essential auth frames from {len(auth_frames_sent)} captured...")
            auth_success = False
            for i, frame in enumerate(auth_frames_sent):
                try:
                    data = json.loads(frame)
                    resource = data.get("req", {}).get("resource", "")
                    
                    # Only replay essential auth frames
                    if not any(r in resource for r in essential_resources):
                        continue
                    
                    data["ts"] = int(time.time() * 1000)
                    await ws.send(json.dumps(data))
                    
                    try:
                        resp = await asyncio.wait_for(ws.recv(), timeout=5)
                        resp_data = json.loads(resp)
                        status = resp_data.get("res", {}).get("statusCode", 0)
                        log(f"  Auth: {resource} -> {status}")
                        
                        if status == 200 and "loginHwId" in resource:
                            auth_success = True
                    except asyncio.TimeoutError:
                        log(f"  Auth: {resource} -> timeout")
                except json.JSONDecodeError:
                    continue
            
            if not auth_success:
                log("AUTH FAILED - loginHwId did not return 200")
                return True  # Signal retry
            
            log("Auth sequence replayed! Starting data collection...")
            
            # Main scraping loop
            consecutive_errors = 0
            
            while True:
                page_num += 1
                log(f"=== Page {page_num} | cursor={cursor_time} ({datetime.fromtimestamp(cursor_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')}) ===")
                
                xs_id = 500 + page_num
                
                request_payload = {
                    "type": "REQUEST",
                    "xs": xs_id,
                    "ts": int(time.time() * 1000),
                    "req": {
                        "method": "GET",
                        "query": {
                            "startTime": 1,
                            "endTime": cursor_time,
                            "order": "DESC",
                            "status": "RESULT,CANCELLED",
                            "contentType": "PLAYLIST",
                            "contentId": CONTENT_ID,
                            "offset": None,
                            "n": 500,
                            "profile": "MOBILE",
                            "calculationId": CALC_ID
                        },
                        "headers": {
                            "Content-Type": "application/json",
                            "clientId": client_id
                        },
                        "resource": "/eventBlocks/find",
                        "basePath": "/api/client/v0.1",
                        "host": "wss://virtual-proxy.virtustec.com"
                    }
                }
                
                try:
                    await ws.send(json.dumps(request_payload))
                    
                    # Wait for matching response
                    response_data = None
                    for _ in range(50):
                        raw = await asyncio.wait_for(ws.recv(), timeout=30)
                        data = json.loads(raw)
                        if data.get("xs") == xs_id:
                            response_data = data
                            break
                    
                    if not response_data:
                        log("  No matching response")
                        consecutive_errors += 1
                        if consecutive_errors >= 5:
                            break
                        continue
                        
                except asyncio.TimeoutError:
                    log("  Timeout")
                    consecutive_errors += 1
                    if consecutive_errors >= 5:
                        break
                    continue
                except websockets.exceptions.ConnectionClosed:
                    log("  WS closed")
                    return True  # Signal reconnect
                
                consecutive_errors = 0
                
                # Parse response
                res = response_data.get("res", {})
                if res.get("statusCode") != 200:
                    log(f"  Status: {res.get('statusCode')}")
                    if res.get("statusCode") == 401:
                        return True  # Need re-auth
                    consecutive_errors += 1
                    continue
                
                body = res.get("body", [])
                if not body:
                    log("  Empty body - done!")
                    break
                
                if isinstance(body, dict):
                    body = [body]
                
                # Process blocks
                matches_this_page = 0
                min_time = cursor_time
                min_league = state.get("min_league", 999999)
                rows = []
                
                for block in body:
                    if not isinstance(block, dict):
                        continue
                    
                    eblock_id = block.get("eBlockId", 0)
                    event_time_str = block.get("eventTime", "")
                    events = block.get("events", [])
                    
                    if not events:
                        continue
                    
                    try:
                        et = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                        event_ts = int(et.timestamp())
                        date_str = et.strftime("%d/%m/%Y %H:%M")
                    except:
                        event_ts = cursor_time - 1
                        date_str = ""
                    
                    if event_ts < min_time:
                        min_time = event_ts
                    if eblock_id < min_league:
                        min_league = eblock_id
                    
                    for ev in events:
                        participants = ev.get("data", {}).get("participants", [])
                        if len(participants) < 2:
                            continue
                        
                        home_team = participants[0].get("fifaCode", "?")
                        away_team = participants[1].get("fifaCode", "?")
                        
                        odd_values = ev.get("data", {}).get("oddValues", [])
                        odd_str = "|".join(str(v) for v in odd_values) if odd_values else ""
                        
                        result_obj = ev.get("result", {})
                        won_markets = result_obj.get("wonMarkets", [])
                        ft_home, ft_away = extract_score_from_won_markets(won_markets)
                        
                        if ft_home is None:
                            continue
                        
                        half_won = result_obj.get("data", {}).get("halfWonMarkets", []) if result_obj.get("data") else []
                        ht_home, ht_away = extract_ht_score(won_markets, half_won)
                        
                        if ft_home > ft_away:
                            result = "H"
                        elif ft_away > ft_home:
                            result = "A"
                        else:
                            result = "D"
                        
                        total_goals = ft_home + ft_away
                        gg = "Y" if ft_home > 0 and ft_away > 0 else "N"
                        match_day = ev.get("order", 0)
                        
                        rows.append([
                            eblock_id, match_day, date_str,
                            home_team, away_team,
                            ft_home, ft_away,
                            ht_home if ht_home is not None else "",
                            ht_away if ht_away is not None else "",
                            result, total_goals, gg, odd_str
                        ])
                        matches_this_page += 1
                
                if rows:
                    with open(OUTPUT_CSV, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(rows)
                
                state["total_matches"] += matches_this_page
                state["cursor_time"] = min_time - 1
                state["page"] = page_num
                state["min_league"] = min_league
                save_state(state)
                
                cursor_time = min_time - 1
                
                log(f"  Collected: {matches_this_page} matches | min_league={min_league} | total={state['total_matches']}")
                
                if min_league <= TARGET_LEAGUE:
                    log(f"DONE! Reached target league {TARGET_LEAGUE}")
                    return False
                
                await asyncio.sleep(1)
    
    except Exception as e:
        log(f"WS connection error: {e}")
        return True
    
    return False


async def main():
    max_retries = 20
    
    for attempt in range(max_retries):
        # Step 1: Capture auth sequence
        client_id, ws_url, auth_sent, auth_recv = await capture_auth_sequence()
        
        if not client_id or not ws_url:
            log(f"Failed to capture auth (attempt {attempt+1})")
            await asyncio.sleep(10)
            continue
        
        # Step 2: Scrape with replayed auth
        needs_retry = await scrape_with_replayed_auth(client_id, ws_url, auth_sent)
        
        if not needs_retry:
            break
        
        log(f"Need to re-authenticate (attempt {attempt+1})")
        await asyncio.sleep(5)
    
    state = load_state()
    log(f"ALL DONE. Total: {state['total_matches']} matches, min league: {state.get('min_league')}")


if __name__ == "__main__":
    asyncio.run(main())
