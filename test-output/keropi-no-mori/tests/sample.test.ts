import { describe, expect, it } from "vitest";

describe("smoke test", () => {
  it("vitest が動作する", () => {
    expect(1 + 1).toBe(2);
  });

  it("DOM 環境が利用できる", () => {
    document.body.innerHTML = '<div id="probe">ok</div>';
    expect(document.getElementById("probe")?.textContent).toBe("ok");
  });
});
