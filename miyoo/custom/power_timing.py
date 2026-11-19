"""Keep the Miyoo's physical POWER duration when input arrives in batches."""
from .patcher import edit

edit("crates/slot-input/src/raw.rs", [
    ('''    Up(Btn),
}''', '''    Up(Btn),
    /// The device measured a continuous POWER hold in its input stream.
    PowerHeld,
}'''),
])

edit("crates/slot-input/src/gesture.rs", [
    ('''            RawEvent::Down(_) => {}
            RawEvent::Up(b) => {''', '''            RawEvent::Down(_) | RawEvent::PowerHeld => {}
            RawEvent::Up(b) => {'''),
    ('''                self.up(b, now)
            }
        }
    }

    pub fn tick''', '''                self.up(b, now)
            }
            RawEvent::PowerHeld => {
                if self.power_down_at.is_none() || self.power_hold_fired {
                    return Vec::new();
                }
                self.power_hold_fired = true;
                vec![Action::PowerHold]
            }
        }
    }

    pub fn tick'''),
])

edit("crates/slot/src/input/evdev.rs", [
    ('''pub fn to_raw(ev: Ev) -> Option<RawEvent> {''', '''/// The kernel's timestamp has the same C long width as decode().
pub fn event_millis(packet: &[u8]) -> Millis {
    let size = TIME_BYTES / 2;
    let seconds = libc::c_long::from_le_bytes(packet[..size].try_into().unwrap());
    let micros = libc::c_long::from_le_bytes(packet[size..TIME_BYTES].try_into().unwrap());
    (seconds.max(0) as Millis).saturating_mul(1000) + micros.max(0) as Millis / 1000
}

pub fn to_raw(ev: Ev) -> Option<RawEvent> {'''),
    ('''use slot_input::{Btn, RawEvent};''', '''use slot_input::{Btn, Millis, RawEvent};'''),
])

edit("crates/slot/src/input/device.rs", [
    ('''use slot_input::{Btn, InputSource, Millis, RawEvent};''',
     '''use slot_input::{Btn, InputSource, Millis, RawEvent, POWER_HOLD_MS};'''),
    ('''    decode, device_name, pick_devices, to_raw, Ev, Hat, EVENT_BYTES, EV_ABS, EV_KEY, EV_SYN,''',
     '''    decode, device_name, event_millis, pick_devices, to_raw, Ev, Hat, EVENT_BYTES, EV_ABS,
    EV_KEY, EV_SYN,'''),
    ('''    let mut hat = Hat::default();
    let mut file = match File::open(node) {''',
     '''    let mut hat = Hat::default();
    let mut power = PowerTiming::default();
    let mut file = match File::open(node) {'''),
    ('''        for ev in buf[..read].chunks_exact(EVENT_BYTES).filter_map(decode) {''',
     '''        for packet in buf[..read].chunks_exact(EVENT_BYTES) {
            let Some(ev) = decode(packet) else { continue };
'''.rstrip()),
    ('''                _ if hall_node => {}
                _ => events.extend(to_raw(ev)),''',
     '''                _ if hall_node => {}
                EV_KEY if ev.code == 116 => power.feed(ev.value, event_millis(packet), &mut events),
                _ => events.extend(to_raw(ev)),'''),
    ('''struct Trace {
''', '''#[derive(Default)]
struct PowerTiming {
    pressed_at: Option<Millis>,
    reported: bool,
}

impl PowerTiming {
    fn feed(&mut self, value: i32, at: Millis, events: &mut Vec<RawEvent>) {
        if value == 1 {
            if self.pressed_at.is_none() {
                self.pressed_at = Some(at);
                self.reported = false;
                events.push(RawEvent::Down(Btn::Power));
            }
            return;
        }

        if matches!(value, 0 | 2) && !self.reported {
            if let Some(since) = self.pressed_at {
                let held_ms = at.saturating_sub(since);
                if held_ms >= POWER_HOLD_MS {
                    self.reported = true;
                    eprintln!("slot: evdev POWER held {held_ms} ms");
                    events.push(RawEvent::PowerHeld);
                }
            }
        }
        if value == 0 {
            self.pressed_at = None;
            events.push(RawEvent::Up(Btn::Power));
        }
    }
}

struct Trace {
'''),
])

edit("crates/slot/src/session.rs", [
    ('''                    RawEvent::Up(b) => self.captured.retain(|x| *x != b),''',
     '''                    RawEvent::Up(b) => self.captured.retain(|x| *x != b),
                    RawEvent::PowerHeld => {}
'''.rstrip()),
])

edit("crates/slot/src/app.rs", [
    ('''        match ev {
            RawEvent::Down(Btn::Menu) if c.first.is_none() => c.menu = true,''',
     '''        match ev {
            RawEvent::PowerHeld => return,
            RawEvent::Down(Btn::Menu) if c.first.is_none() => c.menu = true,'''),
    ('''                Action::PowerTap => return, // OnionOS short-press suspend''',
     '''                Action::PowerTap => {
                    eprintln!("slot: POWER tap; leaving standby to OnionOS");
                    return;
                }'''),
])

edit("crates/slot-input/tests/gesture.rs", [
    ('''#[test]
fn power_release_still_registers_a_hold_if_the_frame_missed_the_tick() {''',
     '''#[test]
fn power_events_processed_in_the_same_frame_preserve_the_kernel_hold() {
    let mut g = gestures();
    let frame = 1000;
    assert_eq!(g.feed(Down(Btn::Power), frame), vec![PowerPress]);
    assert_eq!(g.feed(RawEvent::PowerHeld, frame), vec![PowerHold]);
    assert!(g.feed(RawEvent::PowerHeld, frame).is_empty());
    assert_eq!(g.feed(Up(Btn::Power), frame), vec![PowerOff]);
    assert!(g.tick(frame + POWER_HOLD_MS).is_empty());
}

#[test]
fn power_release_still_registers_a_hold_if_the_frame_missed_the_tick() {'''),
])
