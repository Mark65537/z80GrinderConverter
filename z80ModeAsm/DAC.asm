.z80

FM1_REG_SEL equ 0x4000
FM1_REG_DATA equ 0x4001
FM2_REG_SEL equ 0x4002
FM2_REG_DATA equ 0x4003

DAC_DATA equ 0x2a
DAC_ENABLE equ 0x2b

start:
  ;; Set Yamaha 2612 into DAC mode for channel 6
  ld a, DAC_ENABLE
  ld (FM1_REG_SEL), a
  ld a, 0x80
  ld (FM1_REG_DATA), a

  ;; Turn on channel 6
  ;ld a, 0xb6
  ;ld (FM2_REG_SEL), a
  ;ld a, 0xc0
  ;ld (FM2_REG_DATA), a

  ;; Point to data
  ld ix, data

  ;; Read data and play through DAC
  ld hl, data_end - data
play_loop:
  ld a, DAC_DATA
  ld (FM1_REG_SEL), a
  ld a, (ix)
  ld (FM1_REG_DATA), a
  inc ix
  ;; 4000000MHz / 4000 samples = 1000 cycles delay per sample
  ;; (7 + 13 + 19 + 13 + 10 + 7 + 6 + 4 + 7 + 12) = 98
  ;; (1000 - 98) / 13 = 69 loops
  ld b, 62
play_loop_delay:
  djnz play_loop_delay
  dec hl
  ld a, l
  cp 0
  jr nz, play_loop
  ld a, h
  cp 0
  jr nz, play_loop

  ;; Turn off Yamaha 2612 DAC mode for channel 6
  ld a, DAC_ENABLE
  ld (FM1_REG_SEL), a
  ld a, 0x00
  ld (FM1_REG_DATA), a

while_1:
  jp while_1

data:
  
data_end:

