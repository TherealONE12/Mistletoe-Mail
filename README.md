# Mistletoe Mail

The bakery, post office and toy shop are still lit on Christmas Eve. Watch their windows flash, then ring the same doorbells to make the last deliveries of the night. The route starts with two stops and grows to six. Finish it and the village plays *Jingle Bells*.



This is an 86 × 68 mm, two-layer RP2040 devboard for the Holiday Hardware Swap. Its an simple, hackable Simon says game with a Festive Decoration.

## Play

While the windows fade, tap and release any button. Watch the Lamps. When all three Lamps settle to a steady dim glow, repeat the pattern. A missed stop will trigger the reshow of the pattern. After 45 seconds waiting for a choice, the village returns to its idle glow and the game has stopped.

- **Quiet shift.** While idle, hold POST for a second and release. All three windows flash together, and the Buzzer will no longer play a tune. Repeat to restore sound.
- **Music box.** Hold BAKERY and TOYS while plugging in, then release them after the board starts. The butons play C, E and G. So, you can make your own tunes!


## Inside the village

| Function | Pico GPIO | Circuit |
| --- | --- | --- |
| The lamps | GP2, GP6, GP10 | PWM → 330 Ω → LED anode |
| Matching doorbells | GP4, GP8, GP12 | Internal pull-up|
| Piezo | GP14 | Variable-frequency PWM through 330 Ω |
| J1, top to bottom on front | 3V3, GP20, GP21, GND | Regulated 3.3 V out, I²C0 SDA, I²C0 SCL |

Use 3.3 V accessories at J1 and provide I²C pull-ups on the accessory. The board takes its power from the Pico's USB connector.
[Pico hardware reference](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)
# Mistletoe-Mail
