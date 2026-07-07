# In this program based on the initial data recived, value of rock berm and trench calculates
# open CSV file contains all data from the project. geophysical, metaocenic, geotechnical, ...
# read_input From GDB input file ''inputgeo.xlsx' in the same folderof this excel file
import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox
import os
import math
import csv
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
import array
from token import LPAR
from xml.etree.ElementTree import tostring
import scipy.optimize
from scipy.optimize import curve_fit
import matplotlib.pyplot as plot
import sympy as sp
from sympy.utilities.lambdify import lambdify, implemented_function
from token import LPAR
from xml.etree.ElementTree import tostring
import scipy.optimize
from scipy.optimize import curve_fit



Rw = 1025
g = np.float64(9.81)
v = 0.0000015
SSB = 3

##############################################################
# with open('initial.csv', 'r') as file:
df = pd.read_csv('Hydroinput.csv')
df.columns = ['point_ID', 'SR', 'SP', 'ST', 'FA', 'WL', 'DOC', 'WHS10', 'Tp10', 'CU100', 'WHS100', 'Tp100', 'CU10']
cols_to_skip = ['point_ID', 'ST']
cols_to_convert = [c for c in df.columns if c not in cols_to_skip]
df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='raise')
RD50 = pd.read_csv('RockD50.CSV')
RD50.columns = ['D50']


# ---------------------------------------------------------------------------
# Designe of Rock Berm DHmaxntion for each design code for rock berm
# D50- Height- Slope- top W- bottem W- filter Design
# Section_Deign_rock_berm
def load_file(entry_widget):
    file_path = filedialog.askopenfilename(filetypes=[("CSV or Excel files", "*.csv *.xlsx *.xls")])
    if file_path:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, file_path)
        cols_to_skip = ['point_ID', 'ST']
        cols_to_convert = [c for c in df.columns if c not in cols_to_skip]
        df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='raise')


def start_calculation():
    global RPLWD
    Hydroinput_path = entry_file_path_Hydroinput.get()
    cols_to_skip = ['point_ID', 'ST']
    cols_to_convert = [c for c in df.columns if c not in cols_to_skip]
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='raise')
    RockD50_path = entry_file_path_RockD50.get()


pm = 0.4  # 'pm=('Geometric properties' based on the movement of the particles at the top layer of the soil)
if pm < 0.001:
    r = 0.4
elif pm < 0.01:
    r = 0.6
elif pm < 0.1:
    r = 0.8
elif pm < 0.5:
    r = 1
n = 3  # n=2 to 3
g1 = 0.3  # g1=0.2 to 0.3
gstr = 1 + n * g1
Hydroberm = pd.DataFrame(
    {'point_ID': [], 'D50': [], 'TSh': [], 'Bin': [], 'Hberm': [], 'Alpha': [], 'Wberm': [], 'ABerm': [], 'D50Rock': [],
     'Rrberm': [], 'WD': [], 'BBerm': [], 'NS': [], 'NOD': []})
Hydroberm['WD'] = Hydroberm['WD'].astype(object)
outNR = pd.DataFrame(
    {'point_ID': [], 'SR': [], 'SP': [], 'ST': [], 'WL': [], 'DOC': [], 'WHS10': [], 'Tp10': [], 'CU100': [],
     'WHS100': [], 'Tp100': [], 'CU10': [], 'D50Threshold(m)': [], 'tetashields': [], 'Hberm(m)': [], 'Alpha1:m': [],
     'Wberm(m)': [], 'D50Rock(m)': [], 'Rrberm(kg/m3)': [], 'Hydrodinamic water depth': [], 'NOD': []})
outHR = pd.DataFrame(
    {'point_ID': [], 'SR': [], 'SP': [], 'ST': [], 'WL': [], 'DOC': [], 'WHS10': [], 'Tp10': [], 'CU100': [],
     'WHS100': [], 'Tp100': [], 'CU10': [], 'D50Threshold(m)': [], 'tetashields': [], 'Hberm(m)': [], 'Alpha1:m': [],
     'Wberm(m)': [], 'D50Rock(m)': [], 'Rrberm(kg/m3)': [], 'Hydrodinamic water depth': [], 'NOD': []})
outNR['ST'] = outNR['ST'].astype(object)
outHR['ST'] = outHR['ST'].astype(object)
outNR['Hydrodinamic water depth'] = outNR['Hydrodinamic water depth'].astype(object)
outHR['Hydrodinamic water depth'] = outHR['Hydrodinamic water depth'].astype(object)
in2 = pd.DataFrame(
    {'D50ic2': [], 'D50c2': [], 'Ka1c2': [], 'Ka2c2': [], 'LSc2': [], 'Uwc2': [], 'fcc2': [], 'Awc2': [], 'fwc2': [],
     'TBCWc2': [], 'DDc2': [], 'Tetacrshic2': [], 'D501c2': [], 'ksnc2': [], 'fwnc2': [], 'fcnc2': [], 'TBCWnc2': [],
     'DDnc2': [], 'Tetacrshinc2': [], 'D50nc2': []})
in1 = pd.DataFrame(index=df.index).astype(float)
in3 = pd.DataFrame(index=df.index).astype(float)
in4 = pd.DataFrame(index=df.index).astype(float)

op = pd.DataFrame(index=df.index).astype(float)
opt = pd.DataFrame()

# in1=pd.DataFrame({'D50ic1':[],'D50c1':[],'Ka1c1':[],'Ka2c1':[],'LSc1':[],'Uwc1':[],'fcc1':[],'Awc1':[],'fwc1':[],'TBCWc1':[],'DDc1':[],'Tetacrshic1':[],'D501c1':[],'ksnc1':[],'fwnc1':[],'fcnc1':[],'TBCWnc1':[],'DDnc1':[],'Tetacrshinc1':[],'D50nc1':[],'LS':[]})
SlS = pd.DataFrame(
    {'From Point ID:': [], 'To Point ID:': [], 'SRmean': [], 'SPmean': [], 'Slope stability': [], 'Length': []})
in3 = pd.DataFrame({'C100': [], 'Ts': [], 'HB': [], 'HVR': [], 'NodVR': [], 'DisT': []})
in3['DisT'] = in3['DisT'].astype(object)


# Hydrodynamic stability of seabed based on VanRijn reviesed model
def show_help_file():
    try:
        os.startfile("Manual.pdf")
    except:
        messagebox.showerror("Error", "Cannot open Manual.pdf")


def get_parameters():
    global Dcable, Hmax, NDR, MNod, HDR, TopW, TopWD
    try:
        TopW = float(entry_TopW.get())
        TopWD = float(entry_TopWD.get())
        Dcable = float(entry_Dcable.get())
        MNod = float(entry_MNod.get())
        HDR = float(entry_HDR.get())
        NDR = float(entry_NDR.get())
        Hmax = float(entry_Hmax.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values.")


def load_file(entry_widget):
    file_path = filedialog.askopenfilename(filetypes=[("CSV or Excel files", "*.csv *.xlsx *.xls")])
    if file_path:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, file_path)


def start_calculation():
    opt = pd.DataFrame()
    global RPLWD
    Hydroinput_path = entry_file_path_Hydroinput.get()

    if not Hydroinput_path:
        messagebox.showerror("Error", "Please provide both Hydroinput and D50Rock files.")
        return
    try:
        # Load KP file
        if Hydroinput_path.lower().endswith(".csv"):
            df = pd.read_csv(Hydroinput_path, dtype={3: str})
        else:
            df = pd.read_excel(Hydroinput_path)
        output_dir = "results"
        os.makedirs(output_dir, exist_ok=True)
        # Save calculations
        for i in range(len(df['WL'])):
            print("i", i)
            in1.at[i, 'D50ic1'] = 0.001
            in1.at[i, 'D50c1'] = 1
            in2.at[i, 'D50ic2'] = 0.001
            in2.at[i, 'D50c2'] = 1
            L = 5
            error = 1
            while (error > 0.001):
                in1.at[i, 'LSc1'] = (g * df['Tp10'][i] ** 2 / (2 * np.pi)) * np.tanh(2 * np.pi * df['WL'][i] / L)
                error = abs((in1['LSc1'][i] - L) / in1['LSc1'][i])
                L = in1['LSc1'][i]
            while (in1['D50ic1'][i] < in1['D50c1'][i]):
                in1.at[i, 'Ka1c1'] = np.sin(np.radians(df['FA'][i] - df['SR'][i])) / np.sin(np.radians(df['FA'][i]))
                in1.at[i, 'Ka2c1'] = np.cos(np.radians(df['SP'][i])) * (
                            1 - np.tan(np.radians(df['SP'][i])) ** 2 / np.tan(np.radians(df['FA'][i])) ** 2) ** 0.5
                a1 = 2  # based on the rock berm mixture Norsk Stein minimum D50=67.5 and Ks=D90=1.5D50
                in1.at[i, 'ksc1'] = a1 * in1['D50ic1'][i]  # a1=1.5 to 2
                in1.at[i, 'Uwc1'] = (np.pi * df['WHS10'][i]) / (df['Tp10'][i] * np.sinh(2 * np.pi * df['WL'][i] / in1['LSc1'][i])) # (linear wave theory)
                in1.at[i, 'fcc1'] = 0.24 / (np.log(12 * df['WL'][i] / in1['ksc1'][i])) ** 2
                in1.at[i, 'Awc1'] = (0.5 * df['Tp10'][i] * in1['Uwc1'][i]) / np.pi
                in1.at[i, 'fwc1'] = np.exp(-6 + 5.2 / (in1['Awc1'][i] / in1['ksc1'][i]) ** (0.19))
                in1.at[i, 'TBCWc1'] = 0.125 * Rw * in1['fcc1'][i] * (gstr * df['CU100'][i]) ** 2 + 0.25 * in1['fwc1'][
                    i] * Rw * (gstr * in1['Uwc1'][i]) ** 2
                in1.at[i, 'DDc1'] = in1['D50ic1'][i] * ((NDR / Rw - 1) * g * v ** (-2)) ** (1 / 3)  # DD>0.1
                in1.at[i, 'Tetacrshic1'] = 0.3 / (1 + in1['DDc1'][i]) + 0.055 * (1 - 1 / np.exp(0.02 * in1['DDc1'][i]))
                in1.at[i, 'D50c1'] = in1['TBCWc1'][i] / (
                            (NDR - Rw) * g * in1['Ka1c1'][i] * in1['Ka2c1'][i] * r * in1['Tetacrshic1'][i])
                # calculation of new D50 for check the iterative solution method
                in1.at[i, 'D501c1'] = in1['D50c1'][i] * 0.0005
                in1.at[i, 'ksnc1'] = in1['D501c1'][i] * a1
                in1.at[i, 'fwnc1'] = np.exp(-6 + 5.2 / (in1['Awc1'][i] / in1['ksnc1'][i]) ** (0.19))
                in1.at[i, 'fcnc1'] = 0.24 / (np.log(12 * df['WL'][i] / in1['ksnc1'][i])) ** 2
                in1.at[i, 'TBCWnc1'] = 0.125 * Rw * in1['fcnc1'][i] * (gstr * df['CU100'][i]) ** 2 + 0.25 * \
                                       in1['fwnc1'][i] * Rw * (gstr * in1['Uwc1'][i]) ** 2
                in1.at[i, 'DDnc1'] = (in1['D501c1'][i] * ((NDR / Rw - 1) * g * v ** (-2)) ** (1 / 3))
                in1.at[i, 'Tetacrshinc1'] = 0.3 / (1 + in1['DDnc1'][i]) + 0.055 * (
                            1 - 1 / np.exp(0.02 * in1['DDnc1'][i]))
                in1.at[i, 'D50nc1'] = in1['TBCWnc1'][i] / (
                            (NDR - Rw) * g * in1['Ka1c1'][i] * in1['Ka2c1'][i] * r * in1['Tetacrshinc1'][i])
                if abs(in1['D50nc1'][i] - in1['D50c1'][i]) <= 0.001:
                    in1.at[i, 'D50ic1'] = 0.002
                    break;
                else:
                    in1.at[i, 'D50ic1'] = in1['D50c1'][i]
            L = 5
            error = 1
            while (error > 0.001):
                in2.at[i, 'LSc2'] = (g * df['Tp100'][i] ** 2 / (2 * np.pi)) * np.tanh(2 * np.pi * df['WL'][i] / L)
                error = abs((L - in2['LSc2'][i]) / in2['LSc2'][i])
                L = in2['LSc2'][i]
            while (in2['D50ic2'][i] < in2['D50c2'][i]):
                in2.at[i, 'Ka1c2'] = np.sin(np.radians(df['FA'][i] - df['SR'][i])) / np.sin(np.radians(df['FA'][i]))
                in2.at[i, 'Ka2c2'] = np.cos(np.radians(df['SP'][i])) * (
                            1 - np.tan(np.radians(df['SP'][i])) ** 2 / np.tan(np.radians(df['FA'][i])) ** 2) ** 0.5
                a1 = 2  # based on the rock berm mixture Norsk Stein minimum D50=67.5 and Ks=D90=1.5D50
                in2.at[i, 'ksc2'] = a1 * in2['D50ic2'][i]  # a11=1.5 to 2
                in2.at[i,'Uwc2'] = (np.pi * df['WHS100'][i]) / (df['Tp100'][i] * np.sinh(2 *np.pi * df['WL'][i] / in2['LSc2'][i])) # (linear wave theory)
                in2.at[i, 'fcc2'] = 0.24 / (np.log(12 * df['WL'][i] / in2['ksc2'][i])) ** 2
                in2.at[i, 'Awc2'] = (0.5 * df['Tp100'][i] * in2['Uwc2'][i]) / np.pi
                in2.at[i, 'fwc2'] = np.exp(-6 + 5.2 / ((in2['Awc2'][i] / in2['ksc2'][i]) ** (0.19)))
                in2.at[i, 'TBCWc2'] = 0.125 * Rw * in2['fcc2'][i] * (gstr * df['CU10'][i]) ** 2 + 0.25 * in2['fwc2'][
                    i] * Rw * (gstr * in2['Uwc2'][i]) ** 2
                in2.at[i, 'DDc2'] = in2['D50ic2'][i] * ((NDR / Rw - 1) * g * v ** (-2)) ** (1 / 3)  # DD>0.1
                in2.at[i, 'Tetacrshic2'] = 0.3 / (1 + in2['DDc2'][i]) + 0.055 * (1 - 1 / np.exp(0.02 * in2['DDc2'][i]))
                in2.at[i, 'D50c2'] = in2['TBCWc2'][i] / (
                            (NDR - Rw) * g * in2['Ka1c2'][i] * in2['Ka2c2'][i] * r * in2['Tetacrshic2'][i])
                # calculation of new D50 for check the iterative solution method
                in2.at[i, 'D501c2'] = in2['D50c2'][i] * 0.0005
                in2.at[i, 'ksnc2'] = in2['D501c2'][i] * a1
                in2.at[i, 'fwnc2'] = np.exp(-6 + 5.2 / (in2['Awc2'][i] / in2['ksnc2'][i]) ** (0.19))
                in2.at[i, 'fcnc2'] = 0.24 / (np.log(12 * df['WL'][i] / in2['ksnc2'][i])) ** 2
                in2.at[i, 'TBCWnc2'] = 0.125 * Rw * in2['fcnc2'][i] * (gstr * df['CU10'][i]) ** 2 + 0.25 * in2['fwnc2'][
                    i] * Rw * (gstr * in2['Uwc2'][i]) ** 2
                in2.at[i, 'DDnc2'] = in2['D501c2'][i] * ((NDR / Rw - 1) * g * v ** (-2)) ** (1 / 3)
                in2.at[i, 'Tetacrshinc2'] = 0.3 / (1 + in2['DDnc2'][i]) + 0.055 * (
                            1 - 1 / np.exp(0.02 * in2['DDnc2'][i]))
                in2.at[i, 'D50nc2'] = in2['TBCWnc2'][i] / (
                            (NDR - Rw) * g * in2['Ka1c2'][i] * in2['Ka2c2'][i] * r * in2['Tetacrshinc2'][i])
                if abs(in2['D50nc2'][i] - in2['D50c2'][i]) <= 0.001:
                    in2.at[i, 'D50ic2'] = 0.002
                    break;
                else:
                    in2.at[i, 'D50ic2'] = in2['D50c2'][i]
            if in2['D50c2'][i] > in1['D50c1'][i]:
                Hydroberm.at[i, 'D50'] = in2['D50c2'][i] / 1000
                Hydroberm.at[i, 'TSh'] = in2['Tetacrshinc2'][i]
                Hydroberm.at[i, 'L'] = in2['LSc2'][i]
            else:
                Hydroberm.at[i, 'D50'] = in1['D50c1'][i] / 1000
                Hydroberm.at[i, 'TSh'] = in1['Tetacrshinc1'][i]
                Hydroberm.at[i, 'L'] = in1['LSc1'][i]

        # --------------------------------------------------------------------------
        # Rock Berm DHmaxnsion Design
        def calculate_berm_params(i, RD, D50, T0, KP, WHS100, WL, TSh):
            TSH = Hydroberm['TSh'][i] * D50 * (RD - Rw) / (Hydroberm['D50'][i] * (2650 - Rw))
            hr = df['WHS100'][i] / df['WL'][i]
            if hr < 0.4:
                HB = df['DOC'][i]
            else:
                HB = (abs(1 - TSH / T0)) * df['WL'][i] / 6
            rows = []
            while HB > 2 * D50:
                NS = df['WHS100'][i] / ((RD - Rw) / Rw * 10 * 0.84 * D50)
                NOD = (0.58 - 0.17 * (df['WL'][i]) / (df['WL'][i] - HB)) ** 3 * NS ** 3
                HB = HB - 0.05
                whs100 = WHS100
                wl = WL
                if NOD < MNod:
                    rows.append({
                        'HBerm (m)': HB,
                        'D50': D50,
                        'NOD': NOD,
                        'RD': RD,
                        'i': i,
                        'KP': KP,
                        'whs100': whs100,
                        'wl': wl,
                        'TSH': TSH
                    })

            return pd.DataFrame(rows)

        # In the list bellow based on your project Rock material you can define D50 of the rock

        j = 1
        for i in range(len(df['WL'])):
            print(i)
            if df['ST'][i] == 'Clay':
                in3.at[i, 'C100'] = 0.0022
            elif df['ST'][i] == 'Claysand':
                in3.at[i, 'C100'] = 0.003
            elif df['ST'][i] == 'Siltsand':
                in3.at[i, 'C100'] = 0.0016
            elif df['ST'][i] == 'sandunrippled':
                in3.at[i, 'C100'] = 0.0026
            elif df['ST'][i] == 'sandrippled':
                in3.at[i, 'C100'] = 0.0061
            elif df['ST'][i] == 'Claysandgravel' or 'Sandgravel' or ' Sandshell':
                in3.at[i, 'C100'] = 0.0024
            else:
                in3.at[i, 'C100'] = 0.0047
            T0 = Rw * in3['C100'][i] * df['CU10'][i] ** 2
            D50_list = RD50["D50"].tolist()
            KP = df['point_ID'][i]
            for D50 in D50_list:
                RD = NDR
                # D50_used, HB, NOD = calculate_berm_params(i,RD,  D50, T0)
                opt = pd.concat(
                    [opt, calculate_berm_params(i, RD, D50, T0, KP, df['WHS100'][i], df['WL'][i], Hydroberm['TSh'][i])],
                    ignore_index=True)
                j = j + 1
            for D50 in D50_list:
                RD = HDR
                # D50_used, HB, NOD = calculate_berm_params(i,RD,  D50, T0)
                opt = pd.concat(
                    [opt, calculate_berm_params(i, RD, D50, T0, KP, df['WHS100'][i], df['WL'][i], Hydroberm['TSh'][i])],
                    ignore_index=True)
                opt.at[j, 'whs100'] = df['WHS100'][i]
                opt.at[j, 'wl'] = df['WL'][i]
                j = j + 1
        # End of Rock berm design
        for j in range(len(opt['D50'])):
            print("j", j)
            hr = opt['whs100'][j] / opt['wl'][j]
            T=6000*( opt['TSH'][j])**2+50* opt['TSH'][j]+2.4
            BBerm = T * 0.9  # minimum heght of the rock at top of the cable + cable or CPS Or Seperatore diameter
            Amin = BBerm * 0.9 * 2 / 3
            if 0.2 < hr < 1.5:
                Wberm = TopWD
            else:
                Wberm = TopW
            Alpha = (Amin - Wberm * opt['HBerm (m)'][j]) / opt['HBerm (m)'][j] ** 2
            if Alpha < SSB:
                Alpha = SSB
            ABerm = opt['HBerm (m)'][j] * Wberm + opt['HBerm (m)'][j] ** 2 * Alpha
            z = 1
            while ABerm < Amin:
                Wberm = Wberm * 1.1
                Alpha = (Amin - Wberm * opt['HBerm (m)'][j]) / opt['HBerm (m)'][j] ** 2
                if Alpha < SSB:
                    Alpha = SSB
                ABerm = opt['HBerm (m)'][j] * Wberm + opt['HBerm (m)'][j] ** 2 * Alpha
                z = z + 1
                if z > 20:
                    break
            opt.at[j, 'Alpha 1:m'] = Alpha
            opt.at[j, 'Top Width (m)'] = Wberm
            # opt.at[j, 'point_ID'] = df['point_ID'][j]
            # print (j,opt['i'][j], opt['HBerm (m)'][j], opt['D50'][j],opt['NOD'][j],opt['RD'][j],opt[ 'Alpha 1:m'][j],opt['Top Width (m)'][j])
        file_path = "results/HydrodynamicBerm-design.xlsx"
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            opt.to_excel(writer, sheet_name="Total", index=False)
            outNR.to_excel(writer, sheet_name="Normal density rock", index=False)
            outHR.to_excel(writer, sheet_name="High density rock", index=False)
        messagebox.showinfo("Finished", f"Results saved in folder: {output_dir}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Hydrodynamic design Rock Berm")
width = app.winfo_screenwidth()
height = app.winfo_screenheight()

# Set window size to screen size (but not fullscreen)
app.geometry(f"{width}x{height}+0+0")

ctk.CTkButton(app, text="📘 Read Manual", font=("Times New Roman", 14, "bold"), command=show_help_file).pack(pady=10)
frame_params = ctk.CTkFrame(app)
frame_params.pack(pady=10)
ctk.CTkLabel(frame_params, text="Dcable (m):", font=("Times New Roman", 12, "bold")).grid(row=0, column=0, padx=5,
                                                                                          pady=5)
entry_Dcable = ctk.CTkEntry(frame_params, width=80)
entry_Dcable.grid(row=0, column=1, padx=5, pady=5)
ctk.CTkLabel(frame_params, text="Berm top width Shallow:", font=("Times New Roman", 12, "bold")).grid(row=0, column=2,
                                                                                                      padx=5, pady=5)
entry_TopW = ctk.CTkEntry(frame_params, width=80)
entry_TopW.grid(row=0, column=3, padx=5, pady=5)
ctk.CTkLabel(frame_params, text="Berm top width Deep:", font=("Times New Roman", 12, "bold")).grid(row=0, column=4,
                                                                                                   padx=5, pady=5)

entry_TopWD = ctk.CTkEntry(frame_params, width=80)
entry_TopWD.grid(row=0, column=5, padx=5, pady=5)
ctk.CTkLabel(frame_params, text="Normal Rock density(kg/m3):", font=("Times New Roman", 12, "bold")).grid(row=1,
                                                                                                          column=0,
                                                                                                          padx=5,
                                                                                                          pady=5)
entry_NDR = ctk.CTkEntry(frame_params, width=80)
entry_NDR.grid(row=1, column=1, padx=5, pady=5)
ctk.CTkLabel(frame_params, text="High Rock density(kg/m3):", font=("Times New Roman", 12, "bold")).grid(row=1, column=3,
                                                                                                        padx=5, pady=5)
entry_HDR = ctk.CTkEntry(frame_params, width=80)
entry_HDR.grid(row=1, column=4, padx=5, pady=5)

ctk.CTkLabel(frame_params, text="Maximum Height of Rock Berm(m):", font=("Times New Roman", 12, "bold")).grid(row=2,
                                                                                                              column=0,
                                                                                                              padx=5,
                                                                                                              pady=5)
entry_Hmax = ctk.CTkEntry(frame_params, width=80)
entry_Hmax.grid(row=2, column=1, padx=5, pady=5)
ctk.CTkLabel(frame_params, text="Maximum of Nod:", font=("Times New Roman", 12, "bold")).grid(row=2, column=3, padx=5,
                                                                                              pady=5)
entry_MNod = ctk.CTkEntry(frame_params, width=80)
entry_MNod.grid(row=2, column=4, padx=5, pady=5)
ctk.CTkButton(frame_params, text="Submit", command=get_parameters).grid(row=3, column=2, padx=10, pady=5)
ctk.CTkLabel(app, text="Input Hydroinput details:", font=("Times New Roman", 12, "bold")).pack(pady=5)
entry_file_path_Hydroinput = ctk.CTkEntry(app, width=500)
entry_file_path_Hydroinput.pack(padx=10)
ctk.CTkButton(app, text="Load Hydroinput details file", font=("Times New Roman", 12, "bold"),
              command=lambda: load_file(entry_file_path_Hydroinput)).pack(pady=5)
ctk.CTkLabel(app, text="Input Rock D50 file:", font=("Times New Roman", 12, "bold")).pack(pady=5)
entry_file_path_RockD50 = ctk.CTkEntry(app, width=500)
entry_file_path_RockD50.pack(padx=10)
ctk.CTkButton(app, text="Load Rock D50 file", font=("Times New Roman", 12, "bold"),
              command=lambda: load_file(entry_file_path_RockD50)).pack(pady=5)
ctk.CTkButton(app, text="▶ Start Calculation", command=start_calculation).pack(pady=20)
text_multi = "Please pay attention to the following points when using this tool: \n\n 1- Ensure that all input units are consistent with the system’s primary metric units. \n\n 2- Before using the code, carefully check the structure of the provided Excel or CSV files and place the variable values in the correct columns.\n\n 3- You can refine D50 value of the rock based on the Market or your project limits in input CSV file.\n\n  4- Please make sure to read the provided user guide before using the code.\n\n 5- NOD can be between 0.2 to 7.3 moderate damage is valios for this version of the code \n\n By pressing the 'Read Manual' button at the top of this panel, the PDF guide will open for you."
label = ctk.CTkLabel(app, text=text_multi, font=("Times New Roman", 18))
label.pack(pady=20)

app.mainloop()
