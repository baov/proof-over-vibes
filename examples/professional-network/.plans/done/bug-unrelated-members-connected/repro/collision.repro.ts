// Reproduction of the bug. Not a project test. Run: bash repro/run.sh [current|before]
import { it, expect } from "vitest";
const dir = process.env.CONNECTIONS_SRC ?? new URL("../../../../src/connections/index.ts", import.meta.url).pathname;
const { createConnections, memberId } = await import(dir);

async function scenario() {
  let n = 0;
  const m = createConnections({ ids: { next: () => `req-${++n}` } });
  const [annBo, cy, ann, boCy] = [memberId("ann:bo"), memberId("cy"), memberId("ann"), memberId("bo:cy")];
  const sent = await m.sendRequest(annBo, cy);
  await m.acceptRequest(sent.value.id, cy);
  const state = await m.getPairState(ann, boCy); // step 4, queried before the send: nothing exists between them
  const send = await m.sendRequest(ann, boCy); // step 3
  return { send, state };
}

it("unrelated pair (ann, bo:cy) is not connected and the send succeeds", async () => {
  const { send, state } = await scenario();
  console.log("send:", JSON.stringify(send), "state:", JSON.stringify(state));
  expect(send.ok).toBe(true);
  expect(state.value).toEqual({ connected: false, requestState: "none" });
});
