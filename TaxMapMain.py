#-------------------------------------------------------------------------------
# Name:         Main: Tax Map MXD
# Purpose:      Creates tuple list of units and then iterates through list to
#               call other modules  to create tax  map pdf pages from a template DDP.mxd
#
# Author:      BMay
#
# Created:     05/12/2016
#-------------------------------------------------------------------------------
# Import Modules
import MxdFunctions
import arcpy, os
from arcpy import env
arcpy.env.overwriteOutput = True

# Main Variables #
ws = "C:\\AC\\Projects\\2017TaxMaps\\build"
# Data source for the map books #
gdb = "C:\\AC\\Projects\\2017TaxMaps\\source\\AC_Cadastral.gdb"

# List of Unit Numbers #
DocA = "C:\\AC\\Projects\\2017TaxMaps\\processing\\Lists\\Unum.csv"
# List of Unit Names #
DocB = "C:\\AC\\Projects\\2017TaxMaps\\processing\\Lists\\U_nits.csv"
# List of Locator Frame bounding coordinates
DocC = "C:\\AC\\Projects\\2017TaxMaps\\processing\\Lists\\UnitExtent.csv"
# Mxd to be used as a template #
#mxdP = "C:\\AC\\Projects\\2017TaxMaps\\buildTest\\AerialMXD\\00.mxd"
mxdP = "C:\\AC\\Projects\\2017TaxMaps\\buildTest\\RegMXD\\00.mxd"

# Target FC and FDS vars assigned
fc1 = "AC_Splits2016"
fc2 = "AC_Road_ROWs_Tax"
fc3 = "AC_Subcode"
fc4 = "TaxUnits"
fds1 = "TaxMapToggle"
# Target Fields vars assigned
Calcfld = "InUnit"
# New Field vals assigned
s1 = "Y"
s2 = "N"
# Layer wild cards in the template mxd #
LayerKey1 = "Index"
LayerKey2 = "FocusFrame"
LayerKey3 = "QSIndex"
# strings for FC naming #
string1 = "_Index"
string2 =""
string3 = "_Lbl"
# Path for new PDF
OutPath = "C:\\AC\\Projects\\2017TaxMaps\\buildTest\\p1"

# Define local functions
def group(t,n):
    for i in range(0, len(t),n):
        val = t[i:i+n]
        if len(val)==n:
            yield tuple(val)
################################################################################
# Main Starts here
################################################################################
# Create tuple list of units
with open (DocA, 'r') as a:
    ListA = a.read().rstrip()
    ListA = ListA.splitlines()
with open (DocB, 'r') as b:
    ListB = b.read().rstrip()
    ListB = ListB.splitlines()
with open (DocC, 'r') as c:
    stringC = c.read().rstrip()
    # convert to one line string
    SC = stringC.replace("\n",",")
    # convert one line list into 4 item tuples
    NewTup = list(group(SC.split(','),4))
    # unzip each element of the tuples into separate lists
    xMin = list(zip(*NewTup)[0])
    yMin = list(zip(*NewTup)[1])
    xMax = list(zip(*NewTup)[2])
    yMax = list(zip(*NewTup)[3])
Tuple1 = zip(ListA, ListB, xMin, yMin, xMax, yMax)

# Iterate list to produce tax maps
for tup in Tuple1:
    # Set mxd to Template mxd
    mxd = arcpy.mapping.MapDocument(mxdP)

    # Refresh DDP
    mxd.dataDrivenPages.refresh()
    print "     Unit Number / Name to be processed into a tax map book:    "
    print tup
    # Unit Number assigned
    unum = tup[0]
    # Unit Name assigned
    uname = tup[1]
    unumx = "01"
    xMi = float (tup[2])
    yMi = float (tup[3])
    xMa = float (tup[4])
    yMa = float (tup[5])
    print xMi
    print "Data for unit:   " + uname + " is now being processed"

    # Recalculate field in FC to toggle T F values by unit for synbology class purposes
    # Splits16 field calculation
    MxdFunctions.TogTF(gdb,fds1,fc1,Calcfld,unum,s1,s2)
    # AC_Road_ROW_Simple field calculation
    MxdFunctions.TogTF(gdb,fds1,fc2,Calcfld,unum,s1,s2)
    # AC_Subcode field calculation
    MxdFunctions.TogTF(gdb,fds1,fc3,Calcfld,unum,s1,s2)
    # AC_UnitsOrig field calculation
    MxdFunctions.TogTF(gdb,fds1,fc4,Calcfld,unum,s1,s2)

    # Replace data source in mxd layers from template to next unit
    MxdFunctions.replaceD_Source(mxd,LayerKey1,gdb,uname,string1)

    MxdFunctions.replaceD_Source(mxd,LayerKey2,gdb,uname,string2)

    MxdFunctions.replaceD_Source(mxd,LayerKey3,gdb,uname,string3)

    # Refresh DDP
    mxd.dataDrivenPages.refresh()

    # Set extent of locator frame
    MxdFunctions.MxdLocExtent(mxd,xMi, yMi, xMa, yMa)

    # Refresh DDP

    mxd.dataDrivenPages.refresh()

    # Save Mxd to file
    mxd.saveACopy(os.path.join(ws,unum +".mxd"))

    # Export new mxd to PDF
    MxdFunctions.MxdExport(mxd,OutPath)

    del mxd


