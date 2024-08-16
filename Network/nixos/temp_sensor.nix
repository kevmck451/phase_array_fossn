# Raspberry Pi BME280 Temperature Sensor Configuration

{ config, lib, pkgs, ... }:
{
    enivronment.systemPackages = [
        (python3.withPackages (p: [
            (p.callPackage ./bme280 {})
        ]))
    ];
}