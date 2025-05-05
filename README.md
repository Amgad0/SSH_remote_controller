# SSH Remote Manager

A Python-based GUI application for remotely managing SLA 3d printer machines through SSH. This tool provides a user-friendly interface to configure various settings of the machine remotely.

## Features

- **SSH Connection Management**
  - Connect to a remote machine using SSH
  - Secure password handling
  - Connection status monitoring

- **Pixel Size Configuration**
  - Update X and Y pixel sizes
  - Real-time configuration updates
  - Automatic service restart after changes

- **Mask Image Management**
  - Upload custom mask images
  - Automatic backup of existing masks
  - Support for PNG format

- **Power Settings Control**
  - Configure power values for different areas
  - Update multiple power parameters simultaneously
  - Automatic service restart after changes

## Requirements

- Python 3.x
- Required Python packages:
  - paramiko
  - tkinter
  - json

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd SSH_remote_controller
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### English Version
Run the English version of the application:
```bash
python SSH_remote.py
```

### Chinese Version
Run the Chinese version of the application:
```bash
python SSH_remote_CN.py
```

## Default Settings

- Default Host IP: 192.168.1.111
- Default Username: root
- Default Password: Dentcase
- Default Pixel Size: 66.73 (both X and Y)

## File Structure

- `SSH_remote.py` - Main application file (English version)
- `SSH_remote_CN.py` - Chinese version of the application
- `README.md` - This documentation file

## Building the Application

To build the application into an executable using Nuitka:

1. Install Nuitka:
```bash
pip install nuitka
```

2. Build the English version:
```bash
python -m nuitka --standalone --onefile --enable-plugin=tk-inter --windows-icon-from-ico=Raspberry-Pi-logo-with-SSH-logo4.ico --windows-console-mode=disable SSH_remote.py
```

3. Build the Chinese version:
```bash
python -m nuitka --standalone --onefile --enable-plugin=tk-inter --windows-icon-from-ico=Raspberry-Pi-logo-with-SSH-logo4.ico --windows-console-mode=disable SSH_remote_CN.py
```

The executables will be created in the same directory as the source files.

Note: Make sure the icon file `Raspberry-Pi-logo-with-SSH-logo4.ico` is present in your project directory before building.

## Security Notes

- The application uses SSH for secure remote connections
- Passwords are handled securely through the GUI
- All file transfers are done through SFTP
- The application automatically manages service restarts

## Error Handling

The application includes comprehensive error handling for:
- Connection failures
- File transfer issues
- JSON parsing errors
- Service management problems

## Support

For any issues or questions, please contact the development team.

## License

[Add your license information here] 