import paramiko
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
import threading

class RemoteMachineManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ZyloDent 远程管理器")
        self.root.geometry("300x450")
        
        # Add a progress indicator
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(self.root, textvariable=self.progress_var)
        self.progress_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Disable buttons during operations
        self.operation_in_progress = False
        
        # SSH Connection Frame
        self.conn_frame = ttk.LabelFrame(self.root, text="SSH连接", padding="10")
        self.conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.conn_frame, text="主机IP:").grid(row=0, column=0, sticky=tk.W)
        self.host_ip = tk.StringVar(value="192.168.1.111")
        ttk.Entry(self.conn_frame, textvariable=self.host_ip).grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(self.conn_frame, text="用户名:").grid(row=1, column=0, sticky=tk.W)
        self.username = tk.StringVar(value="root")
        ttk.Entry(self.conn_frame, textvariable=self.username).grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Label(self.conn_frame, text="密码:").grid(row=2, column=0, sticky=tk.W)
        self.password = tk.StringVar()
        ttk.Entry(self.conn_frame, textvariable=self.password, show="*").grid(row=2, column=1, sticky=tk.EW)
        
        # Pixel Size Frame
        self.pixel_frame = ttk.LabelFrame(self.root, text="像素尺寸配置", padding="10")
        self.pixel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.pixel_frame, text="像素尺寸 X:").grid(row=0, column=0, sticky=tk.W)
        self.pixel_size_x = tk.DoubleVar(value=66.73)
        ttk.Entry(self.pixel_frame, textvariable=self.pixel_size_x).grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(self.pixel_frame, text="像素尺寸 Y:").grid(row=1, column=0, sticky=tk.W)
        self.pixel_size_y = tk.DoubleVar(value=66.73)
        ttk.Entry(self.pixel_frame, textvariable=self.pixel_size_y).grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Button(self.pixel_frame, text="更新像素尺寸", command=self.update_pixel_sizes).grid(row=2, column=1, sticky=tk.E)
        
        # Mask Upload Frame
        self.mask_frame = ttk.LabelFrame(self.root, text="遮罩图像上传", padding="10")
        self.mask_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mask_file = tk.StringVar()
        ttk.Label(self.mask_frame, text="已选文件:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(self.mask_frame, textvariable=self.mask_file).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Button(self.mask_frame, text="浏览...", command=self.browse_mask_file).grid(row=1, column=0, sticky=tk.W)
        ttk.Button(self.mask_frame, text="上传遮罩", command=self.upload_mask).grid(row=1, column=1, sticky=tk.E)
        
        # Power Settings Frame
        self.power_frame = ttk.LabelFrame(self.root, text="功率设置", padding="10")
        self.power_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.power_frame, text="功率值:").grid(row=0, column=0, sticky=tk.W)
        self.power_value = tk.IntVar(value=1.0)
        ttk.Entry(self.power_frame, textvariable=self.power_value).grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Button(self.power_frame, text="更新功率设置", command=self.update_power_settings).grid(row=1, column=1, sticky=tk.E)
        
        # Status Bar
        self.status = tk.StringVar(value="就绪")
        ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN).pack(fill=tk.X, padx=10, pady=5)
        
        # Configure grid weights
        for frame in [self.conn_frame, self.pixel_frame, self.mask_frame, self.power_frame]:
            frame.columnconfigure(1, weight=1)
    
    def browse_mask_file(self):
        """Open file dialog to select mask image"""
        filepath = filedialog.askopenfilename(
            title="选择遮罩图像",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        if filepath:
            self.mask_file.set(filepath)
    
    def run_shell_commands(self, ssh, commands):
        """Execute multiple commands in an interactive shell"""
        shell = ssh.invoke_shell()
        shell.settimeout(10)
        
        # Wait for shell to be ready
        time.sleep(0.5)
        while shell.recv_ready():
            shell.recv(1024)
        
        output = ""
        for cmd in commands:
            shell.send(cmd + "\n")
            time.sleep(0.5)
            
            # Wait for command to complete
            while not shell.recv_ready():
                time.sleep(0.1)
            
            # Read output
            while shell.recv_ready():
                output += shell.recv(4096).decode()
        
        shell.close()
        return output
    
    def manage_dent_service(self, ssh, action):
        """Stop or start the dent service with proper waiting"""
        self.status.set(f"{action.capitalize()}ping dent service...")
        self.root.update()
        
        self.run_shell_commands(ssh, [f"systemctl {action} dentpro.service"])
        time.sleep(3)  # Wait for service to properly stop/start
    
    def set_buttons_state(self, state):
        """Enable or disable all operation buttons"""
        for frame in [self.pixel_frame, self.mask_frame, self.power_frame]:
            for child in frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.configure(state=state)

    def run_operation(self, operation_func, *args):
        """Run an operation in a separate thread"""
        if self.operation_in_progress:
            messagebox.showwarning("警告", "另一个操作正在进行中")
            return

        self.operation_in_progress = True
        self.set_buttons_state('disabled')
        self.progress_var.set("操作进行中...")
        
        def thread_func():
            try:
                operation_func(*args)
            except Exception as e:
                error_msg = str(e)  # Capture the error message
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            finally:
                self.root.after(0, self.operation_completed)
        
        thread = threading.Thread(target=thread_func)
        thread.daemon = True
        thread.start()

    def operation_completed(self):
        """Called when an operation is completed"""
        self.operation_in_progress = False
        self.set_buttons_state('normal')
        self.progress_var.set("")
        self.status.set("就绪")

    def update_pixel_sizes(self):
        """Update pixel sizes in machine.json using SFTP"""
        self.run_operation(self._update_pixel_sizes_impl)

    def _update_pixel_sizes_impl(self):
        """Implementation of update_pixel_sizes"""
        pixel_x = self.pixel_size_x.get()
        pixel_y = self.pixel_size_y.get()
        
        ssh = self.create_ssh_connection()
        try:
            # Stop dent service
            self.manage_dent_service(ssh, "stop")
            
            # Open SFTP session
            sftp = ssh.open_sftp()
            json_path = "/root/Dentware/databases/machine.json"
            
            try:
                # Read current JSON
                with sftp.open(json_path, 'r') as remote_file:
                    config = json.load(remote_file)
                
                # Update only the pixel size values while preserving other settings
                config.update({
                    "pixelSizeX": pixel_x,
                    "pixelSizeY": pixel_y
                })
                
                # Write back using SFTP
                with sftp.open(json_path, 'w') as remote_file:
                    json.dump(config, remote_file, indent=4)
                
                self.root.after(0, lambda: self.status.set("像素尺寸更新成功！"))
                self.root.after(0, lambda: messagebox.showinfo("成功", f"已更新像素尺寸 X: {pixel_x}, Y: {pixel_y}"))
            
            except json.JSONDecodeError as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"无效的JSON格式: {str(e)}"))
                self.root.after(0, lambda: self.status.set("错误: 无效的JSON格式"))
            finally:
                sftp.close()
            
            # Restart dent service
            self.manage_dent_service(ssh, "start")
        
        finally:
            ssh.close()

    def upload_mask(self):
        """Upload mask image with proper renaming using shell commands"""
        if not self.mask_file.get():
            messagebox.showerror("错误", "请先选择遮罩文件")
            return
        
        self.run_operation(self._upload_mask_impl)

    def _upload_mask_impl(self):
        """Implementation of upload_mask"""
        ssh = self.create_ssh_connection()
        try:
            # Stop dent service
            self.manage_dent_service(ssh, "stop")
            
            # Prepare file transfer
            sftp = ssh.open_sftp()
            local_path = self.mask_file.get()
            remote_dir = "/root/Dentware/databases/projectorCalibration/"
            remote_path = remote_dir + "mask.png"
            
            try:
                # Rename existing mask if it exists
                try:
                    sftp.stat(remote_path)
                    self.run_shell_commands(ssh, [
                        f"mv {remote_path} {remote_dir}old_mask2.png"
                    ])
                    self.root.after(0, lambda: self.status.set("已将现有遮罩重命名为old_mask2.png"))
                except FileNotFoundError:
                    self.root.after(0, lambda: self.status.set("未找到现有遮罩，继续上传"))
                
                # Upload new mask
                self.root.after(0, lambda: self.status.set(f"正在上传 {os.path.basename(local_path)}..."))
                
                sftp.put(local_path, remote_path)
                self.root.after(0, lambda: self.status.set("遮罩上传成功！"))
                self.root.after(0, lambda: messagebox.showinfo("成功", "遮罩图像上传并重命名成功"))
            
            finally:
                sftp.close()
            
            # Restart dent service
            self.manage_dent_service(ssh, "start")
        
        finally:
            ssh.close()

    def update_power_settings(self):
        """Update power settings in projectorAdaptivePower.json using shell commands"""
        self.run_operation(self._update_power_settings_impl)

    def _update_power_settings_impl(self):
        """Implementation of update_power_settings"""
        power_value = self.power_value.get()
        
        ssh = self.create_ssh_connection()
        try:
            # Stop dent service
            self.manage_dent_service(ssh, "stop")
            
            # Get the current file content
            sftp = ssh.open_sftp()
            json_path = "/root/Dentware/databases/projectorAdaptivePower.json"
            
            try:
                # Read current JSON
                with sftp.open(json_path, 'r') as remote_file:
                    config = json.load(remote_file)
                
                # Update only the specific power values while preserving other settings
                config.update({
                    "smallArea": power_value,
                    "smallAreaOffset": power_value,
                    "normalArea": power_value,
                    "normalAreaOffset": power_value,
                    "largeAreaPower": power_value
                })
                
                # Write back using SFTP
                with sftp.open(json_path, 'w') as remote_file:
                    json.dump(config, remote_file, indent=4)
                
                self.root.after(0, lambda: self.status.set("功率设置更新成功！"))
                self.root.after(0, lambda: messagebox.showinfo("成功", f"所有功率值已设置为 {power_value}"))
            
            except json.JSONDecodeError as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"无效的JSON格式: {str(e)}"))
                self.root.after(0, lambda: self.status.set("错误: 无效的JSON格式"))
            finally:
                sftp.close()
            
            # Restart dent service
            self.manage_dent_service(ssh, "start")
        
        finally:
            ssh.close()
    
    def create_ssh_connection(self):
        """Create and return an SSH connection"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        
        host = self.host_ip.get()
        username = self.username.get()
        password = self.password.get()

        if not all([host, username]):
            raise ValueError("请填写所有连接字段")
        
        self.status.set(f"正在连接到 {host}...")
        self.root.update()
        
        ssh.connect(host, username=username, password=password, timeout=10)
        return ssh

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteMachineManager(root)
    root.mainloop()