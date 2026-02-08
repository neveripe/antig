# Energy Data Processor - User Guide

**A simple, step-by-step guide to view graphs of your electricity usage**

This guide will help you download your energy data from ESB Networks and view it as graphs on your computer. No technical knowledge required!

---

## 📋 What You'll Need

- A computer with an internet connection
- Your ESB Networks account login details
- A web browser (Chrome, Firefox, Edge, or Safari)

> **Don't have an ESB Networks account?** You'll need to register first at [www.esbnetworks.ie](https://www.esbnetworks.ie/) by clicking "Register Now" when you see the login screen. This guide assumes you already have an account.

---

## Part 1: Download Your Energy Data from ESB Networks

Follow these steps **exactly** as written:

### Step 1: Go to ESB Networks Website

1. Open your web browser
2. Type this address in the address bar: **www.esbnetworks.ie**
3. Press **Enter** on your keyboard

### Step 2: Login to Your Account

1. Look at the **top right** of the page
2. Click on the **icon that looks like a person** (this is your "Account" button)
3. You'll see two empty boxes:
   - **First box**: Type your email address or username
   - **Second box**: Type your password
4. Click the blue **"Sign In"** button

> **Trouble logging in?** Make sure your CAPS LOCK is off and you're typing your password correctly. If you forgot your password, click "Forgot Password" below the login boxes.

### Step 3: Go to Energy Consumption Section

1. After signing in, look for a button or link that says **"My energy consumption"**
2. Click on it

### Step 4: Download Your Data File

1. Look across the top of the page for tabs (like tabs in a filing cabinet)
2. Click on the tab labeled **"Downloads"**
3. You'll see several download options
4. Click on **"30-minute readings in calculated kWh"**
5. Wait a few seconds - your file will download automatically

> **Where did it go?** The file is in your "Downloads" folder. The filename starts with **HDF_calkWh_** followed by some numbers.

---

## Part 2: Open and Copy Your Data

### Step 5: Find Your Downloaded File

1. Open **File Explorer** (Windows) or **Finder** (Mac)
   - **Windows**: Click the folder icon in your taskbar, OR press the Windows key + E
   - **Mac**: Click the Finder icon in your dock
2. Click on **"Downloads"** in the left sidebar
3. Look for a file that starts with **HDF_calkWh_** (it should be at the top if you just downloaded it)

### Step 6: Open the File with Notepad/TextEdit

**For Windows:**
1. **Right-click** on the HDF_calkWh file
2. Move your mouse to **"Open with"**
3. Click **"Notepad"**
4. The file will open showing lots of rows of data

**For Mac:**
1. **Right-click** (or Control-click) on the HDF_calkWh file
2. Move your mouse to **"Open With"**
3. Click **"TextEdit"**
4. The file will open showing lots of rows of data

### Step 7: Copy ALL the Data

1. With the file open in Notepad/TextEdit, click anywhere inside the window
2. Press **Ctrl + A** (Windows) or **⌘ Cmd + A** (Mac) to select everything
   - The text should turn blue/highlighted
3. Press **Ctrl + C** (Windows) or **⌘ Cmd + C** (Mac) to copy it

> **Important:** Make sure ALL the text is selected (highlighted in blue) before copying!

---

## Part 3: Use the Energy Processor Tool

### Step 8: Open the Energy Processor

1. Find the file called **index.html** in the **dist** folder
   - This should be inside the **web** folder where you saved/installed the Energy Processor
   - If someone sent you the file, look where they told you to save it
   - If you downloaded it, check your Downloads folder
2. **Double-click** the index.html file
3. It will open in your web browser
4. Wait **10-15 seconds** for the page to fully load
   - You'll know it's ready when you see: **"✅ Ready to process your energy data"**

> **Can't find the file?** Ask the person who gave you this tool where they saved the index.html file. It should be in a folder called "web" then "dist".

### Step 9: Paste Your Data

1. On the webpage, you'll see two tabs at the top:
   - **📁 Upload CSV** 
   - **📋 Paste Data**
2. Click on **"📋 Paste Data"** (the second tab)
3. You'll see a large empty box with example text in gray
4. Click inside this box
5. Press **Ctrl + V** (Windows) or **⌘ Cmd + V** (Mac) to paste your data
   - Your data should fill the box
6. Click the green button that says **"✅ Process Pasted Data"**

### Step 10: Wait for Processing

1. You'll see a message saying **"⏳ Processing pasted data..."**
2. Wait a few seconds (usually 2-5 seconds)
3. The page will show **"✅ Data processed successfully!"** with how many readings were loaded

### Step 11: View Your Graph

**The graph appears automatically!** You should now see:

- **A colorful graph** showing your electricity usage over time
  - **Blue line** = Electricity you used (imported from the grid)
  - **Orange line** = Electricity you exported (if you have solar panels)
- **Statistics boxes** showing:
  - Total Readings
  - Total Import (kWh)
  - Total Export (kWh)
  - Net Consumption (kWh)

### Step 12: Adjust the Date Range (Optional)

If you want to see a specific time period:

1. Look for the **"⚙️ Configure"** section above the graph
2. You'll see two date pickers:
   - **Start Date**: Click and choose the first day you want to see
   - **End Date**: Click and choose the last day you want to see
3. Click the **"Generate Graph"** button
4. The graph will update to show only that time period

---

## 🎉 You're Done!

You should now see your energy usage as a graph. You can:

- **Zoom in/out** on the graph by scrolling your mouse wheel
- **Pan around** by clicking and dragging on the graph
- **Hover over points** to see exact values
- **Change dates** to view different time periods

---

## ❓ Troubleshooting

### "The page won't load" or "Shows an error"

- **Wait longer** - The first load can take up to 15 seconds
- **Check your internet** - The page needs to download some files from the internet the first time
- **Refresh the page** - Press F5 on your keyboard
- **Try a different browser** - Chrome or Firefox work best

### "❌ This doesn't look like CSV data"

- Make sure you copied the **entire** file (use Ctrl+A / Cmd+A)
- Make sure you opened the file in **Notepad** or **TextEdit**, not Excel
- The data should have commas and many rows

### "❌ No data in selected date range"

- Check that your **End Date** is **after** your **Start Date**
- Make sure the dates are within the range of your downloaded data

### "The graph looks wrong" or "No graph appears"

- Scroll down - the graph might be below where you're looking
- Try clicking "Generate Graph" again
- Refresh the page (F5) and paste your data again

---

## 💡 Tips

- **Save your CSV file** - Keep the HDF_calkWh file so you don't have to download it again
- **Download regularly** - ESB Networks typically has your last 2 years of data available
- **Compare time periods** - Try different date ranges to compare summer vs. winter usage
- **No installation needed** - This tool runs entirely in your browser, nothing is uploaded to the internet

---

## 🆘 Need More Help?

If you're still having trouble:

1. Take a screenshot of any error messages (Press **PrtScn** on keyboard)
2. Note exactly which step you're stuck on
3. Contact the person who set this up for you

---

**Privacy Note:** 🔒 Your data never leaves your computer. Everything is processed locally in your web browser. No data is sent to the internet or stored anywhere except on your computer.
