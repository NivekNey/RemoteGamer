# RemoteGamer

To have a controller plugged into a remote machine.

## Roles

* `Remote`: Like TV's remote control, I am have the remote control. 
* `Station`: I have the game, I am the gaming station.

## Install

### I am the `Remote`

```bash
pip install -e .[remote]
```

### I am the `Station`

```bash
pip install -e .[station]
```

## How to use

### I am the `Remote`

```bash
$ # wait for Station to be up first, CAPTURE_IP is the ip of the Station
$ remotegamer remote --host=${CAPTURE_IP}
```

### I am the `Station`

```bash
$ remotegamer station
```

## Known bugs

* Xbox button check has false positives sometimes.

