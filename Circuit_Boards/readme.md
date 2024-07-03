# Circuit Board Information

---
## Using Mics with Antennas
- the mic symbol on the mic modules should be facing away from center when connected
- before soldering mic pins to modules, check that the INMP441 chip is correctly placed from factory
    - discard any that are not correctly aligned

---
## Ethernet Cable Configuration
- RJ45 Ethernet connectors and cabling are used to connect the microphone antennas to the fpga shield
- making the cables from scratch allowed for exact cable lengths
- the antennas were designed to optimize the configuration of the mic module pins
- in the initial testing phase, the standard TIA 568B coloring configuration was used
- this caused issues with certain data channels due to the twisted pair configuration
- the ethernet cables were reconfigured to fix this issue
- if you wanted to use standard ethernet cables, you will need to reroute the mic antenna pins
- and reassign the fpga shield pins as well

### Standard Ethernet Configuration
~~~
Twisted Pairs
- Orange Stripe: ws
- Orange: d3 <--- This channel is corrupted because of ws

- Green Stripe: d1
- Green: gnd

- Blue Stripe: d2
- Blue: pwr

- Brown Stripe: clk
- Brown: d4 <--- This channel is corrupted because of clk
~~~

### Custom Ethernet Configuration
~~~
Twisted Pairs
- Orange Stripe: ws
- Orange: pwr

- Green Stripe: d3
- Green: d1

- Blue Stripe: clk
- Blue: gnd

- Brown Stripe: d2
- Brown: d4
~~~

#### Top

| Orange Stripe | Green | Brown Stripe | Blue Stripe |
|---------------|-------|--------------|-------------|

#### Bottom

| Green Stripe | Orange | Blue | Brown |
|--------------|--------|------|-------|

#### Left to Right
| ws  | d3  | d1  | pwr | d2  | gnd | clk | d4  |
|-----|-----|-----|-----|-----|-----|-----|-----|
| os  | gs  | g   | o   | brs | b   | bs  | br  |