// Pointer picking on the 3D floor: hover and click on the invisible boxes around each agent and desk.
import * as THREE from "three";

export function createPicker({ canvas, camera, targets, onHover, onSelect }) {
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();

  function roleAt(event) {
    const rect = canvas.getBoundingClientRect();
    ndc.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    const hit = raycaster.intersectObjects(targets, false)[0];
    return hit ? hit.object.userData.role : null;
  }

  let down = null;
  canvas.addEventListener("pointermove", (event) => {
    const role = roleAt(event);
    canvas.style.cursor = role ? "pointer" : "default";
    onHover(role, event);
  });
  canvas.addEventListener("pointerleave", () => onHover(null, null));
  canvas.addEventListener("pointerdown", (event) => { down = { x: event.clientX, y: event.clientY }; });
  canvas.addEventListener("pointerup", (event) => {
    // A click, not the end of a drag.
    if (down && Math.hypot(event.clientX - down.x, event.clientY - down.y) < 5) onSelect(roleAt(event));
    down = null;
  });
}
