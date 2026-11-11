// Server-sent events from /events. EventSource reconnects by itself after a drop.
export function connect(onSnapshot, onStatus) {
  const source = new EventSource("/events");
  source.onopen = () => onStatus("live");
  source.onmessage = (event) => {
    onStatus("live");
    onSnapshot(JSON.parse(event.data));
  };
  source.onerror = () => onStatus("reconnecting");
}
