# Visuelt kontrollerede formler fra EL-materialet

## W04 Ladning Q [C]
Kilde: EL03:4,10, EL13:12
Formel: $Q=I\Delta t$
Betingelse: Konstant strøm; ellers sum af delintervaller.

## I01 Strøm I [A]
Kilde: EL02:9-11
Formel: $I=\frac{U}{R}$
Betingelse: Ohmsk R; DC eller konsistente AC-magnituder.

## I02 Strøm I [A]
Kilde: EL02:10, EL13:13,17
Formel: $I=\frac{P}{U}$
Betingelse: Stationær DC; P er elektrisk indgangseffekt.

## I03 Strømmens størrelse |I| [A]
Kilde: EL02:10, EL13:13,16
Formel: $|I|=\sqrt{\frac{P}{R}}$
Betingelse: Ohmsk resistans; P er tabet i R.

## I04 Middelstrøm I [A]
Kilde: EL02:7, EL03:4
Formel: $I_{\mathrm{middel}}=\frac{Q}{\Delta t}$
Betingelse: Netto passeret ladning i valgt interval.

## I05 Kildestrøm I [A]
Kilde: EL04:3-4
Formel: $I=\frac{E}{r_i+R}$
Betingelse: Én DC-kilde med intern serie-modstand.

## I06 Grenstrøm Ik [A]
Kilde: EL04:6-7, EL09:3-10
Formel: $I_k=\frac{U_{\mathrm{gren}}}{R_k}$
Betingelse: Parallelgrene har samme knudespænding.

## I07 Grenstrøm I1 [A]
Kilde: EL04:7
Formel: $I_1=I_{\mathrm{total}}\frac{R_2}{R_1+R_2}$
Betingelse: To parallelle ohmske modstande.

## B10 Viklingsstrøm I [A]
Kilde: EL05:3, EL06:9-12
Formel: $I=\frac{Hl}{N}$
Betingelse: Magnetisk vej/spole-model som B05.

## N02 Ukendt grenstrøm Ix [A]
Kilde: EL08:2, EL09:3-4
Formel: $I_x=\sum I_{\mathrm{ind}}-\sum I_{\mathrm{andre,ud}}$
Betingelse: KCL i én knude; stationær kreds.

## U01 Spænding U [V]
Kilde: EL02:9-11
Formel: $U=R I$
Betingelse: Ohmsk belastning; U følger valgt polaritet.

## U02 Spænding U [V]
Kilde: EL02:10, EL13:13
Formel: $U=\frac{P}{I}$
Betingelse: Stationær DC; samme komponent for P og I.

## U03 Spændingens størrelse |U| [V]
Kilde: EL02:10, EL13:13,15
Formel: $|U|=\sqrt{P R}$
Betingelse: Effekt afsat i ohmsk R.

## U04 Potentialforskel U [V]
Kilde: EL13:11-12, EL02:5
Formel: $U=\frac{W}{Q}$
Betingelse: Elektrisk energi overført pr. ladning.

## U05 Klemspænding Ukl [V]
Kilde: EL04:3
Formel: $U_{\mathrm{kl}}=E-I r_i$
Betingelse: Afladning; I ud af kildens pluspol.

## U06 Delspænding U1 [V]
Kilde: EL04:5
Formel: $U_1=U\frac{R_1}{R_1+R_2}$
Betingelse: To serie-R; midtpunktet er ubelastet.

## U07 Knudespænding Va [V]
Kilde: EL09:4-10, EL08:4-10
Formel: $V_a=\frac{\sum_k E_k/R_k}{\sum_k 1/R_k}$
Betingelse: Fælles knude a og reference 0; kilder + mod a.

## E01 Induceret spænding e [V]
Kilde: EL14:3-5, EL12:3
Formel: $e_{\mathrm{middel}}=-N\frac{\Delta\Phi}{\Delta t}$
Betingelse: Middel-EMK over interval; samme flux gennem hver vinding.

## E02 Øjebliks-EMK e(t) [V]
Kilde: EL14:4,8
Formel: $e(t)=-N\frac{\mathrm{d}\Phi}{\mathrm{d}t}$
Betingelse: Valgt positiv fluxnormal og konsistent omløbsretning.

## E03 Bevægelses-EMK |E| [V]
Kilde: EL12:3-4
Formel: $|E|=Blv$
Betingelse: Lige leder; l, v og B står indbyrdes vinkelret.

## E05 Selvinduktions-EMK es [V]
Kilde: EL14:7-9
Formel: $e_s=-L\frac{\mathrm{d}i}{\mathrm{d}t}$
Betingelse: Konstant induktans; induceret modspænding.

## N01 Knudespændinger Va [V]
Kilde: EL08:2-10, EL09:3-10
Formel: $\sum_b\frac{V_a-V_b}{R_{ab}}=I_{\mathrm{ind},a}$
Betingelse: DC-net; strømmene ud af hver ukendt knude.

## N03 Kontrol af spændinger
Kilde: EL08:3,9-14, EL09:3-10
Formel: $\sum_k\Delta V_k=0$
Betingelse: KVL i lukket DC-sløjfe; kontrol efter KCL-løsning.

## R01 Resistans R [Ω]
Kilde: EL02:8-11
Formel: $R=\frac{U}{I}$
Betingelse: Ohmsk komponent ved den aktuelle temperatur.

## R02 Resistans R [Ω]
Kilde: EL02:10, EL13:15
Formel: $R=\frac{P}{I^2}$
Betingelse: Ohmsk R; P er dens afsatte effekt.

## R03 Resistans R [Ω]
Kilde: EL02:10, EL13:13
Formel: $R=\frac{U^2}{P}$
Betingelse: Ohmsk R; U måles over R.

## R04 Ledermodstand R [Ω]
Kilde: EL07:3-5,8
Formel: $R=\rho\frac{l}{S}$
Betingelse: Ensartet leder; ρ ved relevant temperatur.

## R05 Varm modstand RT [Ω]
Kilde: EL10:3-5
Formel: $R_T=R_t[1+\alpha_t(T-t)]$
Betingelse: Lineær metalmodel; α hører til referencen t.

## R06 Kold modstand Rt [Ω]
Kilde: EL10:9-10
Formel: $R_t=\frac{R_T}{1+\alpha_t(T-t)}$
Betingelse: Samme lineære model og reference som R05.

## R07 Seriemodstand Rs [Ω]
Kilde: EL04:4-5,8
Formel: $R_s=\sum_{k=1}^{n}R_k$
Betingelse: Én strømvej; samme strøm i alle R.

## R08 Parallelmodstand Rp [Ω]
Kilde: EL04:6-8
Formel: $R_p=\left(\sum_{k=1}^{n}\frac{1}{R_k}\right)^{-1}$
Betingelse: Alle R mellem de samme to knuder.

## R09 Indre modstand ri [Ω]
Kilde: EL04:3,8
Formel: $r_i=\frac{E-U_{\mathrm{kl}}}{I}$
Betingelse: Belastet DC-kilde; afladning.

## R10 Resistans R [Ω]
Kilde: EL07:6
Formel: $R=\frac{1}{G}$
Betingelse: Ohmsk komponent.

## G03 Resistivitet ρ
Kilde: EL07:3,6
Formel: $\rho=\frac{R S}{l}$
Betingelse: Ensartet leder ved kendt temperatur.

## G04 Tværsnit S [mm²]
Kilde: EL07:3,8
Formel: $S=\rho\frac{l}{R}$
Betingelse: Ensartet leder; kendt materialeværdi.

## G05 Lederlængde l [m]
Kilde: EL07:3,8
Formel: $l=\frac{R S}{\rho}$
Betingelse: Ensartet leder.

## G06 Temperaturstigning ΔT [K]
Kilde: EL10:5,8
Formel: $\Delta T=\frac{R_T-R_t}{R_t\alpha_t}$
Betingelse: Lineær metalmodel med kendt t.

## G01 Konduktans G [S]
Kilde: EL07:6,9
Formel: $G=\frac{1}{R}=\frac{I}{U}$
Betingelse: Samme ohmske komponent.

## G02 Specifik ledningsevne γ
Kilde: EL07:6,9
Formel: $\gamma=\frac{1}{\rho}$
Betingelse: Materialeværdi ved samme temperatur.

## P01 Elektrisk effekt P [W]
Kilde: EL13:6,12-13
Formel: $P=U I$
Betingelse: Stationær DC; forbrugerens pluspol mod strømpilen.

## P02 Varmeeffekt P [W]
Kilde: EL13:12-15
Formel: $P=I^2R$
Betingelse: Ohmsk R ved aktuel temperatur.

## P03 Varmeeffekt P [W]
Kilde: EL13:12-13
Formel: $P=\frac{U^2}{R}$
Betingelse: U er spændingen over ohmsk R.

## P04 Middel-effekt P [W]
Kilde: EL13:6-7,17
Formel: $P_{\mathrm{middel}}=\frac{W}{\Delta t}$
Betingelse: Energi/arbejde omsat i et interval.

## P05 Afgiven effekt Pud [W]
Kilde: EL13:4
Formel: $P_{\mathrm{ud}}=\eta P_{\mathrm{ind}}$
Betingelse: Samme maskine og driftspunkt.

## P06 Effekttab Ptab [W]
Kilde: EL13:4
Formel: $P_{\mathrm{tab}}=P_{\mathrm{ind}}-P_{\mathrm{ud}}$
Betingelse: Stationær energibalance.

## P07 Virkningsgrad η [1]
Kilde: EL13:4
Formel: $\eta=\frac{P_{\mathrm{ud}}}{P_{\mathrm{ind}}}$
Betingelse: Stationær drift; eller samme energiperiode.

## P08 Mekanisk effekt P [W]
Kilde: EL13:10,17
Formel: $P=M\omega=M\frac{2\pi n}{60}$
Betingelse: Rotation; n er omdrejninger pr. minut i sidste udtryk.

## W01 Energi W [J] eller [kWh]
Kilde: EL13:7-8,13,16
Formel: $W=P t$
Betingelse: Konstant effekt i hele perioden.

## W02 Elektrisk energi W [J]
Kilde: EL13:11-12
Formel: $W=UQ=UIt$
Betingelse: Konstant spænding; ved UIt også konstant I.

## W03 Tid t [s]
Kilde: EL13:17
Formel: $t=\frac{W}{P}$
Betingelse: Konstant effekt.

## W05 Brændselsenergi W [MJ]
Kilde: EL13:9
Formel: $W=H_u m\quad\mathrm{eller}\quad W=H_u V$
Betingelse: Kildens omregningstabel; samme brændsel og reference.

## M01 Løftearbejde W [J]
Kilde: EL13:5,14,18
Formel: $W=mgh$
Betingelse: Roligt løft; ændringen i potentiel energi.

## M02 Arbejde W [J]
Kilde: EL13:5
Formel: $W=Fs$
Betingelse: Konstant kraft parallelt med bevægelsen.

## M05 Rotationsarbejde W [J]
Kilde: EL13:10,15
Formel: $W=M\theta$
Betingelse: Konstant moment.

## M03 Moment M [N·m]
Kilde: EL13:10,15
Formel: $M=Fr$
Betingelse: Kraften står vinkelret på armen.

## M04 Vinkelhastighed ω [rad/s]
Kilde: EL13:10,15
Formel: $\omega=\frac{\Delta\theta}{\Delta t}=2\pi n$
Betingelse: Konstant rotation; ellers middelværdi.

## M06 Moment M [N·m]
Kilde: EL13:10,17
Formel: $M=\frac{P_{\mathrm{mek}}}{\omega}=\frac{60P_{\mathrm{mek}}}{2\pi n}$
Betingelse: Mekanisk aksel-effekt og omdrejningshastighed.

## F01 Elektrisk kraft |F| [N]
Kilde: EL03:5,7,9
Formel: $|F|=\frac{|Q_1Q_2|}{4\pi\varepsilon a^2}$
Betingelse: Punktladninger i ensartet isotropt medium.

## F02 Elektrisk feltstyrke Ef [V/m]
Kilde: EL03:8-10
Formel: $E_f=\frac{F}{Q},\qquad |E_f|=\frac{|Q_k|}{4\pi\varepsilon a^2}$
Betingelse: F/Q er feltet på prøveladningen; a ved punktkilden.

## F03 Kraft F [N]
Kilde: EL03:8,10
Formel: $\vec F=Q\vec E_f$
Betingelse: Prøveladning i givet elektrisk felt.

## F04 Afstand a [m]
Kilde: EL03:7,10
Formel: $a=\sqrt{\frac{|Q_1Q_2|}{4\pi\varepsilon |F|}}$
Betingelse: Samme punktladningsmodel som F01.

## F05 Ukendt ladning |Q2| [C]
Kilde: EL03:10
Formel: $|Q_2|=\frac{4\pi\varepsilon a^2|F|}{|Q_1|}$
Betingelse: Punktladninger; fortegnet afgøres af tiltrækning/frastødning.

## F06 Elektrisk flux Ψ [V·m]
Kilde: EL03:9
Formel: $\Psi=E_f A=\frac{Q}{\varepsilon}$
Betingelse: Ensartet normalt felt; eller lukket kugle i ensartet medium.

## F07 Permittivitet ε [F/m]
Kilde: EL03:7,9
Formel: $\varepsilon=\varepsilon_0\varepsilon_r$
Betingelse: Lineært isotropt medium.

## B01 Magnetisk flux Φ [Wb]
Kilde: EL01:10-11, EL12:2, EL14:8
Formel: $\Phi=BA$
Betingelse: Ensartet felt vinkelret på fladen.

## B02 Fluxtæthed B [T]
Kilde: EL01:11, EL05:2-3
Formel: $B=\frac{\Phi}{A}$
Betingelse: Ensartet felt; A er areal normalt på feltet.

## B03 Fluxtæthed B [T]
Kilde: EL05:3, EL06:9-12, EL11:3-4,8
Formel: $B=\mu H$
Betingelse: Lineær materiale-model med kendt μ.

## B04 Felt om lang leder B [T]
Kilde: EL01:12-13
Formel: $B=\frac{\mu I}{2\pi a}$
Betingelse: Lang, lige leder; punkt uden for lederen.

## B05 Magnetisk feltstyrke H [A/m]
Kilde: EL05:3, EL06:9
Formel: $H=\frac{NI}{l}=\frac{F_m}{l}$
Betingelse: Ensartet magnetisk vej; ringkerne/længere spole-model.

## B06 Magnetomotorisk kraft Fm [A]
Kilde: EL05:2, EL06:5-8
Formel: $F_m=NI=R_m\Phi$
Betingelse: Amperevindingstal i magnetkredsmodellen.

## B07 Reluktans Rm [A/Wb]
Kilde: EL05:2, EL06:6,13, EL11:3
Formel: $R_m=\frac{l}{\mu A}$
Betingelse: Ensartet magnetisk segment; lineær μ.

## B08 Flux Φ [Wb]
Kilde: EL05:2, EL06:6,8,13
Formel: $\Phi=\frac{NI}{R_m}$
Betingelse: Lukket lineær magnetkreds; lækage negligeres.

## B09 Permeabilitet μ [H/m]
Kilde: EL06:10-11, EL11:3
Formel: $\mu=\mu_0\mu_r=\frac{B}{H}$
Betingelse: Lineært medium eller sekantværdi ved givet driftspunkt.

## B11 Magnetkredsens areal A [m²]
Kilde: EL05:2, EL06:6
Formel: $A=\frac{\Phi}{B}$
Betingelse: Ensartet felt normalt på kernens tværsnit.

## B12 Feltstyrke H [A/m]
Kilde: EL05:3, EL11:4,8
Formel: $H=\frac{B}{\mu}$
Betingelse: Lineær materiale-model ved kendt μ.

## B13 Relativ permeabilitet μr [1]
Kilde: EL06:10-11
Formel: $\mu_r=\frac{\mu}{\mu_0}$
Betingelse: Samme enhed for absolutte permeabiliteter.

## E04 Induktans L [H]
Kilde: EL14:8-9
Formel: $L=\frac{N^2\mu A}{l}$
Betingelse: Lineær ensartet spole/magnetkreds; lækage negligeres.

## E06 Induktans L [H]
Kilde: EL14:8
Formel: $L=-\frac{e_s\Delta t}{\Delta I}$
Betingelse: Lineær strømrampe; tab adskilt fra selvinduktion.

## K01 Kraft på leder |F| [N]
Kilde: EL16:3-5,7
Formel: $|F|=B|I|l$
Betingelse: Leder vinkelret på ensartet magnetfelt.

## K02 Aktiv lederlængde l [m]
Kilde: EL16:7
Formel: $l=\frac{|F|}{B|I|}$
Betingelse: Leder vinkelret på B.

## K03 Fluxtæthed B [T]
Kilde: EL16:7
Formel: $B=\frac{|F|}{|I|l}$
Betingelse: Leder vinkelret på feltet.

## K04 Kraft mellem ledere |F| [N]
Kilde: EL15:2,4
Formel: $|F|=\frac{\mu|I_1I_2|l}{2\pi a}$
Betingelse: Lange parallelle ledere; a er centerafstand.

