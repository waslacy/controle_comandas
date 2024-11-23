# RF433 Call System

This project is a **call management system** for restaurants or similar establishments, developed with **Python** and **Arduino**. It integrates RF433 controllers to register tables, allowing them to notify waitstaff when assistance is needed by pressing a button.

## Features
- **Table Registration**: Each RF433 controller is linked to a table number.
- **Real-Time Notifications**: When a button is pressed, the system logs the call and displays it.
- **Customizable Settings**: Configuration for call intervals, alerts, and Arduino connection via a GUI.
- **Intuitive Interface**: Built with CustomTkinter for a clean and dynamic user experience.
- **Visual Alerts**: Displays active calls on the main screen with timestamps.

## Requirements
- **Python Libraries**:
  - `customtkinter`
  - `PIL`
  - `ctypes`
  - `serial`
  - `json`
  - `datetime`
- **Hardware**:
  - RF433 controller
  - Arduino board

## Usage
1. **Setup**: Ensure the Arduino is connected to the correct port and listed in `config.json`.
2. **Register Controllers**: Assign each controller button to a table or waiter action via the configuration screen.
3. **Operation**: Start the system, and monitor calls in real-time.

## Customization
All settings, including intervals and alert configurations, are easily adjustable via the GUI.

---

## License
Copyright 2024 Tecleweb®  
Todos os direitos reservados.  
Este software não pode ser usado, copiado, modificado ou redistribuído sem permissão explícita.