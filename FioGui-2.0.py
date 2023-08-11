import os
import subprocess
import Tkinter as tk
import tkFileDialog as filedialog
from ttk import Progressbar, Combobox

def run_fio_command():
    # Get user inputs from GUI
    traddr = traddr_entry.get()
    size = size_entry.get()
    rw = rw_combobox.get()
    bs = bs_entry.get()
    iodepth = iodepth_entry.get()
    spdkpath = spdkpath_entry.get()

    # Validate inputs (you can add more validation if needed)
    if not all((spdkpath, traddr, size, rw, bs, iodepth)):
        result_label.config(text="Please fill in all fields.", fg="red")
        return

    # Change to the spdk directory and execute setup.sh
    spdk_directory = spdkpath
    setup_script = './scripts/setup.sh'

    try:
        os.chdir(spdk_directory)
        subprocess.check_call(setup_script, shell=True)
    except subprocess.CalledProcessError as e:
        result_label.config(text="Error occurred during setup: {}".format(e), fg="red")
        return

    # Run the fio command and pick the output
    fio_command = (
        'LD_PRELOAD={}/build/fio/spdk_nvme '
        'fio --filename="trtype=PCIe traddr={} ns=1" '
        '--name=fiotest --size={} --rw={} --bs={} '
        '--numjobs=1 --ioengine=spdk --iodepth={} --thread=1'
    ).format(spdk_directory, traddr, size, rw, bs, iodepth)

    # Add the progress bar
    progress_bar = Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.grid(row=8, column=0, columnspan=2, pady=10)

    try:
        # Show the progress bar while the command is running
        progress_bar.start()

        # Execute the fio command
        subprocess.check_call(fio_command, cwd=spdk_directory, shell=True)
        
        # Stop the progress bar after the command is executed
        progress_bar.stop()

        output_file = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=rw, title="Save FIO Output")

        if output_file:
            result_label.config(text="Fio Command executed successfully.\nOutput saved to {}.".format(output_file), fg="#006400")
        else:
            result_label.config(text="Fio Command executed successfully.", fg="#006400")

    except subprocess.CalledProcessError as e:
        progress_bar.stop()
        result_label.config(text="Error occurred during fio execution: {}".format(e), fg="red")

# Create the GUI
root = tk.Tk()
root.title("FIO_SPDK-2.0")

# window size
window_width = 600
window_height = 400
root.geometry("{}x{}".format(window_width, window_height))

# Styling
font_style = ("Arial", 12)
label_color = "#333333"
entry_color = "#666666"
button_color = "#009900" 

# Add padding between walls and lines
label_pad_y = 10
entry_pad_y = 5
button_pad_y = 20
left_padding = 40  
top_padding = 40   

def browse_spdk_path():
    selected_path = filedialog.askdirectory()
    if selected_path:
        spdkpath_entry.delete(0, tk.END)  
        spdkpath_entry.insert(0, os.path.join(selected_path, "spdk")) 

spdkpath_label = tk.Label(root, text="Path to SPDK", font=font_style, fg=label_color, anchor='w')
spdkpath_label.grid(row=0, column=0, pady=(top_padding, label_pad_y), padx=left_padding, sticky='w')

spdkpath_entry = tk.Entry(root, font=font_style, fg=entry_color)
spdkpath_entry.grid(row=0, column=1, pady=(top_padding, entry_pad_y), padx=5, sticky='w')

browse_button = tk.Button(root, text="Browse", font=font_style, command=browse_spdk_path)
browse_button.grid(row=0, column=2, pady=(top_padding, entry_pad_y), padx=5, sticky='w')
traddr_label = tk.Label(root, text="PCI address of the Disk", font=font_style, fg=label_color, anchor='w')
traddr_label.grid(row=1, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
traddr_entry = tk.Entry(root, font=font_style, fg=entry_color)
traddr_entry.grid(row=1, column=1, pady=entry_pad_y, padx=5, sticky='w')

size_label = tk.Label(root, text="Size", font=font_style, fg=label_color, anchor='w')
size_label.grid(row=2, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
size_entry = tk.Entry(root, font=font_style, fg=entry_color)
size_entry.grid(row=2, column=1, pady=entry_pad_y, padx=5, sticky='w')

rw_options = ["read", "write", "randread", "randwrite"]

rw_label = tk.Label(root, text="Specify Read/Write command", font=font_style, fg=label_color, anchor='w')
rw_label.grid(row=3, column=0, pady=label_pad_y, padx=left_padding, sticky='w')

rw_combobox = Combobox(root, values=rw_options, font=font_style, state="readonly")
rw_combobox.grid(row=3, column=1, pady=entry_pad_y, padx=5, sticky='w')
rw_combobox.set(rw_options[0])  

bs_label = tk.Label(root, text="Block size", font=font_style, fg=label_color, anchor='w')
bs_label.grid(row=4, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
bs_entry = tk.Entry(root, font=font_style, fg=entry_color)
bs_entry.grid(row=4, column=1, pady=entry_pad_y, padx=5, sticky='w')

iodepth_label = tk.Label(root, text="IO depth", font=font_style, fg=label_color, anchor='w')
iodepth_label.grid(row=5, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
iodepth_entry = tk.Entry(root, font=font_style, fg=entry_color)
iodepth_entry.grid(row=5, column=1, pady=entry_pad_y, padx=5, sticky='w')

run_button = tk.Button(root, text="Run FIO", font=font_style, bg=button_color, command=run_fio_command)
run_button.grid(row=6, column=0, columnspan=2, pady=button_pad_y)

result_label = tk.Label(root, text="", font=font_style, fg="black")
result_label.grid(row=7, column=0, columnspan=2, pady=label_pad_y)

root.mainloop()
