with open("main.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip_mode = False
for line in lines:
    if "async def inspect_screen()" in line:
        skip_mode = True
        continue
    if skip_mode:
        # Stop skipping when we hit the next major function or end of file
        if line.startswith("def ") or (line.startswith("async def ") and "inspect_screen" not in line) or line.startswith("@app."):
            skip_mode = False
            new_lines.append(line)
        continue
    if not skip_mode:
        new_lines.append(line)

# Append the correct clean function at the end
clean_func = """
@app.post("/inspect")
async def inspect_screen():
    global active_bridge_ws
    if not active_bridge_ws:
        raise HTTPException(status_code=400, detail="Local PC Bridge is not connected via WebSocket")
    try:
        await active_bridge_ws.send(json.dumps({"action": "inspect_screen", "params": {}}))
        response_data = await asyncio.wait_for(active_bridge_ws.recv(), timeout=6.0)
        return json.loads(response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screen inspection failed: {str(e)}")
"""

with open("main.py", "w") as f:
    f.writelines(new_lines)
    f.write("\n" + clean_func)

print("SUCCESS: Inspect block completely replaced cleanly!")
