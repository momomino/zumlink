# ZUM Radio Optimization Scripts

This repo contains scripts for optimizing the parameters of ZUM link radios based on the levels measured by the radios.


## Scripts

### Optimize Data Rate

Currently this script instantiates a number of radios based on IP address, then checks the signal margin against the minimum threshold and updates the data rates of all the radios (in specified order) in order to optimize data throughput and reliability of data link.


## Modules

[Zumlink Module](./zumlink/Readme.md)