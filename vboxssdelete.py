import os
import re
import shlex
import subprocess

import clr
clr.AddReference('System.Windows.Forms')

# .NET imports
import wpf
import System
from System.Windows import Application, Controls, Forms, Window

class VBoxSSDelete(Window):
    vbmpaths = ["C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
                "C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe",
                "C:\Program Files\VirtualBox\VBoxManage.exe",
                "C:\Program Files (x86)\VirtualBox\VBoxManage.exe" ]
    
    def __init__(self):
        wpf.LoadComponent(self, 'vboxssdelete.xaml')

        self.VBoxManageButton.Click += self.VBoxManageButtonClick
        self.DeleteButton.Click += self.DeleteButtonClick
        self.VMListBox.SelectionChanged += self.VMListBoxChange

        for path in self.vbmpaths:
            if os.path.exists(path):
                self.VBoxManageTextBox.Text = path
                break
        
        self.LoadVMList()
        
    def LoadVMList(self):
        try:
            self.VMListBox.Items.Clear()
                       
            cmd = '"%s" list vms' % self.VBoxManageTextBox.Text
            vmslist = subprocess.check_output(cmd)
                    
            for line in str.splitlines(vmslist):
                # vboxmanage list vms result is 'machine_name {uuid}'
                (name, uuid) = shlex.split(line)
                
                lbi = Controls.ListBoxItem()
                lbi.Content = name
                self.VMListBox.Items.Add(lbi)
        except Exception as err:
            raise err
        
    def LoadSSList(self, name):
        """
        Get list of snapshots for given machine name/uuid
        """
        
        try:
            self.SSListBox.Items.Clear()
            
            cmd = '"%s" showvminfo "%s"' % (self.VBoxManageTextBox.Text, name)
            cmdoutput = subprocess.check_output(cmd)
            
            found_snapshot_string = False
            for line in str.splitlines(cmdoutput):
                if line.strip() == "":
                    continue
                
                if re.match("Snapshots:", line):
                    found_snapshot_string = True
                    continue
                
                if found_snapshot_string:
                    mobj = re.match("\s*Name: (.*) \(UUID: (.*)\)", line)
                    if mobj:
                        lbi = Controls.ListBoxItem()
                        lbi.Content = mobj.group(1)
                        self.SSListBox.Items.Add(lbi)
                    # no more snapshots found, exit loop
                    else:
                        break
                    
        except Exception as err:
            raise err

    def VBoxManageButtonClick(self, sender, args):
        ofd = Forms.OpenFileDialog()
        ofd.CheckFileExists = True
        if ofd.ShowDialog() == Forms.DialogResult.OK:
            self.VBoxManageTextBox.Text = ofd.FileName

    def VMListBoxChange(self, sender, args):
        self.LoadSSList(self.VMListBox.SelectedItem.Content)
        
    def DeleteButtonClick(self, sender, args):
        for item in self.SSListBox.SelectedItems:
            cmd = '"%s" snapshot "%s" delete "%s"' % (self.VBoxManageTextBox.Text,
                                                      self.VMListBox.SelectedItem.Content, 
                                                      item.Content)
            self.StatusTextBox.Text += "Deleting snapshot with command command [%s]\n" % (cmd)
            cmdoutput = subprocess.check_output(cmd)
            self.StatusTextBox.Text += cmdoutput + "\n"

        self.LoadSSList(self.VMListBox.SelectedItem.Content)
            