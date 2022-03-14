import dearpygui.dearpygui as dpg
from themes import create_theme_imgui_light ,create_theme_client, create_theme_server
from Serial import mySerial


class serial_ui():
    CLIENT_THEME = None
    SERVER_THEME = None

    def __init__(self):
        self.my_serial = mySerial()
        self.portList  = self.my_serial.get_availabile_port_list()
        self.SELECTED_DEVICE = ""
        self.dpg_setup()
        self.create_primary_window()
        serial_ui.CLIENT_THEME = create_theme_client()
        serial_ui.SERVER_THEME = create_theme_server()
        self.dpg_show_view_port()
        LIGHT_THEME = create_theme_imgui_light()
        dpg.bind_item_theme(self.prime_window, LIGHT_THEME)

        dpg.set_primary_window(self.prime_window, True)
        while dpg.is_dearpygui_running():
            if self.my_serial.connected:
                recv_msg = self.my_serial.read_serial()
                if recv_msg:
                    max_length = 122
                    if len(recv_msg) > max_length:
                        truncated_msg = recv_msg[0:122-3] + "..."
                        self.log_msg(truncated_msg, serial_ui.SERVER_THEME)
                    else:
                        self.log_msg(recv_msg, serial_ui.SERVER_THEME)
                    print(f"Received: {recv_msg}")
                    self.log_msg(recv_msg, serial_ui.SERVER_THEME)
            try:
                dpg.render_dearpygui_frame()
            except KeyboardInterrupt:
                return
            dpg.set_exit_callback(self.exit_callback)
        self.dpg_cleanup()

    def update_ports_callback(self):
        portList = self.my_serial.get_availabile_port_list()
        dpg.configure_item("__listPortsTag", items=portList)


    def create_ui_msg_column(self):
        with dpg.group(horizontal=True):
            dpg.add_text(default_value="Message: ")
            user_msg = dpg.add_input_text(tag="usrMsgTxt", default_value="help", width=755)
            dpg.add_button(tag="sendMsgBtn", label="Send",
                callback=self.send_msg_to_serial_port_callback, user_data={'userMsgTag': user_msg})

    def create_column_above_logger(self):
        with dpg.group(horizontal=True):
            # Clear button
            dpg.add_button(label="Clear", callback=lambda: dpg.delete_item(self.filter_id, children_only=True))
            # Filter Text
            dpg.add_input_text(callback=lambda sender: dpg.set_value(self.filter_id, dpg.get_value(sender)), width=819)

    def create_logger_window(self):
        ## this creates a window at bottom
        child_logger_id = dpg.add_child_window(tag="logger", width=870, height=340)
        self.filter_id = dpg.add_filter_set(parent=child_logger_id)


    def create_primary_window(self):
        with dpg.window(tag="Primary Window", autosize=True) as self.prime_window:
            with dpg.group(horizontal=True):
                dpg.add_button(tag="avPortsBtn", label="Refresh Available Ports", callback=self.update_ports_callback)
                # After clicking it will show a list view of ports
                if not self.portList:
                    dpg.add_listbox(["No Ports available"], tag="__listPortsTag", width=300,
                            num_items=-1, callback=self.selected_port_callback)
                else:
                    dpg.add_listbox(self.portList, tag="__listPortsTag", width=300,
                        num_items=2, callback=self.selected_port_callback)
            self.create_ui_msg_column()
            self.create_column_above_logger()
            self.create_logger_window()

    def dpg_setup(self):
        dpg.create_context()
        windowWidth  = 895
        windowHeight = 450
        dpg.create_viewport(title='Serial GUI', width=windowWidth, height=windowHeight)
        dpg.setup_dearpygui()

    def selected_port_callback(self, Sender):
        self.SELECTED_DEVICE = dpg.get_value(Sender).split(' ')[0]
        self.my_serial.connect(self.SELECTED_DEVICE)
        print(f"User selected: {self.SELECTED_DEVICE}")


    def dpg_show_view_port(self):
        dpg.set_viewport_resizable(False)
        dpg.show_viewport()

    def dpg_start_dearpygui(self):
        dpg.start_dearpygui()

    def dpg_cleanup(self):
        dpg.destroy_context()

    def exit_callback(self):
        dpg.stop_dearpygui()

    def send_msg_to_serial_port_callback(self, sender, app_data, user_data) -> None:
        """
        Callbacks may have up to 3 arguments in the following order.

        sender:
        the id of the UI item that submitted the callback

        app_data:
        occasionally UI items will send their own data (ex. file dialog)

        user_data:
        any python object you want to send to the function
        """
        if not self.SELECTED_DEVICE:
            print("User is not selected any device.")
        if not self.my_serial.connected:
            print("Device is not connected")
        msg_to_send = dpg.get_value(user_data['userMsgTag'])
        if not msg_to_send:
            print("No message.")
        else:
            self.my_serial.write_to_serial(msg_to_send)
            self.log_msg(msg_to_send, serial_ui.CLIENT_THEME)
            print(f"Sent |{msg_to_send}| to {self.SELECTED_DEVICE}")
            dpg.configure_item("usrMsgTxt", default_value="")


    def log_msg(self, message, custom_theme):
        new_log = dpg.add_text(message, parent=self.filter_id, filter_key=message)
        dpg.bind_item_theme(new_log, custom_theme)

