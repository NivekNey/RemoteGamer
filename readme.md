# RemoteGamer

To have a controller plugged into a remote machine.

## Install

### I capture

```bash
pip install -e .[capture]
```

### I replay

```bash
pip install -e .[replay]
```

## How to use

### I capture

```bash
$ remotegamer Capture
```

### I replay

```bash
$ remotegamer Replay --host=${CAPTURE_IP}
```

## Known bugs

* Xbox button check has false positives sometimes.

## Todo

* Test on actual remote machine
* Block device event if possible when capture is on
