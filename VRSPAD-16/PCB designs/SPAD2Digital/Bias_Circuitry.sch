EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr User 5315 4134
encoding utf-8
Sheet 18 37
Title "Quantum Random Number Generator"
Date "2021-09-27"
Rev "v2.1"
Comp "University of California, Santa Barbara"
Comment1 "Biomimetic Circuits and Nanosystems Group"
Comment2 "Zachary Nelson"
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 1750 900  2    50   Input ~ 0
TIA_REF
Text GLabel 3650 900  2    50   Input ~ 0
COMP_REF
Text GLabel 950  900  0    50   Input ~ 0
3.3V
Text GLabel 1350 1500 3    50   Input ~ 0
GND
Wire Wire Line
	950  900  1000 900 
Wire Wire Line
	1350 1450 1350 1500
Text GLabel 850  1850 2    50   Input ~ 0
3.3V
Text GLabel 850  2250 2    50   Input ~ 0
GND
$Comp
L Device:C C110
U 1 1 611D582E
P 800 2050
F 0 "C110" H 915 2096 50  0000 L CNN
F 1 "4.7u" H 915 2005 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 838 1900 50  0001 C CNN
F 3 "~" H 800 2050 50  0001 C CNN
	1    800  2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	800  1900 800  1850
Wire Wire Line
	800  1850 850  1850
Wire Wire Line
	800  2200 800  2250
Wire Wire Line
	800  2250 850  2250
$Comp
L Custom_Part_Library:LTC3045 U32
U 1 1 610E1018
P 1350 1100
F 0 "U32" H 1350 1615 50  0000 C CNN
F 1 "LTC3045" H 1350 1524 50  0000 C CNN
F 2 "Package_DFN_QFN:DFN-10-1EP_3x3mm_P0.5mm_EP1.65x2.38mm" H 1150 1500 50  0001 C CNN
F 3 "" H 1150 1500 50  0001 C CNN
	1    1350 1100
	1    0    0    -1  
$EndComp
Wire Wire Line
	1700 1000 1700 900 
Wire Wire Line
	1750 900  1700 900 
Connection ~ 1700 900 
Wire Wire Line
	1000 1000 950  1000
Wire Wire Line
	950  1000 950  900 
Wire Wire Line
	1700 1100 1750 1100
Text GLabel 1750 1100 2    50   Input ~ 0
3.3V
Wire Wire Line
	1000 1200 1000 1500
Wire Wire Line
	1000 1500 1350 1500
$Comp
L Device:C C108
U 1 1 610E9289
P 2100 1350
F 0 "C108" H 2215 1396 50  0000 L CNN
F 1 "4.7u" H 2215 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 2138 1200 50  0001 C CNN
F 3 "~" H 2100 1350 50  0001 C CNN
	1    2100 1350
	1    0    0    -1  
$EndComp
Connection ~ 1350 1500
Text GLabel 1350 1850 2    50   Input ~ 0
TIA_REF
Text GLabel 1350 2250 2    50   Input ~ 0
GND
$Comp
L Device:C C111
U 1 1 610EF077
P 1300 2050
F 0 "C111" H 1415 2096 50  0000 L CNN
F 1 "10u" H 1415 2005 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 1338 1900 50  0001 C CNN
F 3 "~" H 1300 2050 50  0001 C CNN
	1    1300 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	1300 2200 1300 2250
Wire Wire Line
	1300 2250 1350 2250
Wire Wire Line
	1300 1900 1300 1850
Wire Wire Line
	1300 1850 1350 1850
Text GLabel 2850 900  0    50   Input ~ 0
3.3V
Text GLabel 3250 1500 3    50   Input ~ 0
GND
Wire Wire Line
	2850 900  2900 900 
Wire Wire Line
	3250 1450 3250 1500
Wire Wire Line
	3600 1000 3600 900 
Wire Wire Line
	3650 900  3600 900 
Wire Wire Line
	2900 1000 2850 1000
Wire Wire Line
	2850 1000 2850 900 
Wire Wire Line
	3600 1100 3650 1100
Text GLabel 3650 1100 2    50   Input ~ 0
3.3V
Wire Wire Line
	2900 1200 2900 1500
Wire Wire Line
	2900 1500 3250 1500
$Comp
L Device:C C109
U 1 1 610FCE0C
P 4000 1350
F 0 "C109" H 4115 1396 50  0000 L CNN
F 1 "4.7u" H 4115 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4038 1200 50  0001 C CNN
F 3 "~" H 4000 1350 50  0001 C CNN
	1    4000 1350
	1    0    0    -1  
$EndComp
Connection ~ 3250 1500
Connection ~ 3600 900 
$Comp
L Custom_Part_Library:LTC3045 U33
U 1 1 610FCDF9
P 3250 1100
F 0 "U33" H 3250 1615 50  0000 C CNN
F 1 "LTC3045" H 3250 1524 50  0000 C CNN
F 2 "Package_DFN_QFN:DFN-10-1EP_3x3mm_P0.5mm_EP1.65x2.38mm" H 3050 1500 50  0001 C CNN
F 3 "" H 3050 1500 50  0001 C CNN
	1    3250 1100
	1    0    0    -1  
$EndComp
Text GLabel 3100 1850 2    50   Input ~ 0
3.3V
Text GLabel 3100 2250 2    50   Input ~ 0
GND
$Comp
L Device:C C112
U 1 1 611079EB
P 3050 2050
F 0 "C112" H 3165 2096 50  0000 L CNN
F 1 "4.7u" H 3165 2005 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 3088 1900 50  0001 C CNN
F 3 "~" H 3050 2050 50  0001 C CNN
	1    3050 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	3050 1900 3050 1850
Wire Wire Line
	3050 1850 3100 1850
Wire Wire Line
	3050 2200 3050 2250
Wire Wire Line
	3050 2250 3100 2250
Text GLabel 3600 2250 2    50   Input ~ 0
GND
$Comp
L Device:C C113
U 1 1 611079FB
P 3550 2050
F 0 "C113" H 3665 2096 50  0000 L CNN
F 1 "10u" H 3665 2005 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 3588 1900 50  0001 C CNN
F 3 "~" H 3550 2050 50  0001 C CNN
	1    3550 2050
	1    0    0    -1  
$EndComp
Wire Wire Line
	3550 2200 3550 2250
Wire Wire Line
	3550 2250 3600 2250
Wire Wire Line
	3550 1900 3550 1850
Wire Wire Line
	3550 1850 3600 1850
Text GLabel 3600 1850 2    50   Input ~ 0
COMP_REF
Wire Wire Line
	1700 1200 2100 1200
Wire Wire Line
	1350 1500 2050 1500
Wire Wire Line
	3600 1200 4000 1200
Wire Wire Line
	3250 1500 4000 1500
$Comp
L Device:R_POT_US RV1
U 1 1 61550F86
P 2050 1650
F 0 "RV1" H 1983 1696 50  0000 R CNN
F 1 "30k" H 1983 1605 50  0000 R CNN
F 2 "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical" H 2050 1650 50  0001 C CNN
F 3 "~" H 2050 1650 50  0001 C CNN
	1    2050 1650
	1    0    0    -1  
$EndComp
Connection ~ 2050 1500
Wire Wire Line
	2050 1500 2100 1500
Wire Wire Line
	2200 1650 2450 1650
Wire Wire Line
	2450 1650 2450 1200
Wire Wire Line
	2450 1200 2100 1200
Connection ~ 2100 1200
$Comp
L Device:R_POT_US RV2
U 1 1 615533B6
P 4250 1650
F 0 "RV2" H 4183 1696 50  0000 R CNN
F 1 "30k" H 4183 1605 50  0000 R CNN
F 2 "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical" H 4250 1650 50  0001 C CNN
F 3 "~" H 4250 1650 50  0001 C CNN
	1    4250 1650
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 1500 4250 1500
Connection ~ 4000 1500
Wire Wire Line
	4400 1650 4400 1200
Wire Wire Line
	4400 1200 4000 1200
Connection ~ 4000 1200
$EndSCHEMATC
