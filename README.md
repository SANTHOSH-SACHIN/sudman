# Sudman - Systemd User Daemon Manager

A user-friendly command-line tool to manage systemd user units. Sudman provides a simpler interface compared to the standard `systemctl` commands, making it easier to list, start, stop, enable, and disable systemd user units.

## Features

- List all systemd user units with color-coded status information
- Filter units by type (service, timer, etc.)
- Start, stop, and restart units
- Enable and disable units for autostart
- View unit status with detailed information
- View unit logs with configurable number of lines
- User-friendly output formatting with color support

## Installation

### Using pip

```bash
pip install git+https://github.com/SANTHOSH-SACHIN/sudman.git
```

### Using uv

```bash
uv pip install sudman
```

### From source

```bash
git clone https://github.com/SANTHOSH-SACHIN/sudman.git
cd sudman
uv pip install -e .
```

## Usage

```
usage: sudman [-h] [--version] {list,status,start,stop,restart,enable,disable,logs} ...

Systemd User Daemon Manager - A user-friendly interface for systemd user units

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

Command to run:
  {list,status,start,stop,restart,enable,disable,logs,interactive}
    list                List systemd user units
    status              Show status of a unit
    start               Start a unit
    stop                Stop a unit
    restart             Restart a unit
    enable              Enable a unit
    disable             Disable a unit
    logs                Show logs for a unit
    interactive         Start interactive TUI mode
```

### Examples

List all user units:
```bash
sudman list
```

List only service units:
```bash
sudman list --type service
```

Show status of a specific unit:
```bash
sudman status my-service.service
```

Start a unit:
```bash
sudman start my-service.service
```

Stop a unit:
```bash
sudman stop my-service.service
```

Enable a unit (for autostart):
```bash
sudman enable my-service.service
```

View logs for a unit:
```bash
sudman logs my-service.service
```

View more log lines:
```bash
sudman logs my-service.service --lines 100
```

Start interactive mode:
```bash
sudman interactive
```

## Release Notes

### v0.2.0

- Added interactive TUI mode (`sudman interactive`)
- Improved error handling and user feedback
- Added more comprehensive unit tests
- Updated documentation and help text
- Various bug fixes and stability improvements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
