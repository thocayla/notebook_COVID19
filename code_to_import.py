# coding: utf-8

# ### Script Python permettant de suivre l'évolution de la covid-19 selon les données hospitalières
# 
# * **Source** : https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/
# * **Exemple** : https://www.gouvernement.fr/info-coronavirus/carte-et-donnees
# * **Scope** : Granularité jour
# * **Auteur** : Thomas Cayla
# * **Update** : 09/11/2020

## Load libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display
sns.set_style("whitegrid") #set the grid style

## Parametric variables
filename     = 'https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7'
format_date  = '%Y-%m-%d'
legend       = False
figsize      = (16,12)
fontweight   = 'bold'
fontsize     = 16
labelsize    = fontsize-3
x_interval   = 10 #days
y_interval   = 2500
ha           = 'center'
textcoords   = 'offset points'
arrowprops   = {'arrowstyle': '|-|,widthA=0.2,widthB=0.2', }
cible        = 5000

## Import data
data = pd.read_csv(filename,sep=';')
data = data[data.sexe==0].drop(['dep','sexe'],axis=1).sort_values(by='jour').reset_index(drop=True)
data.jour = pd.to_datetime(data.jour, format=format_date)
data_sum = data.groupby('jour').sum() # Somme des données par jour
data_sum = data_sum.rename(columns={'dc': 'dc_cumul'})
data_sum['dc_non_cumul'] = data_sum.dc_cumul-data_sum.dc_cumul.shift(1).fillna(0)
data_sum.dc_non_cumul = data_sum.dc_non_cumul.astype(int)
#print('Nombre de jours = '+str(data_sum.shape[0]))

## Jupyter Widgets
def data_to_plots():
    print('Choisissez les données que vous souhaitez visualiser :')
    hosp = widgets.Checkbox(
        value=True,
        description='Patients hospitalisés',
        disabled=False,
        indent=False
    )
    rea = widgets.Checkbox(
        value=True,
        description='Personnes en réanimation',
        disabled=False,
        indent=False
    )
    rad = widgets.Checkbox(
        value=False,
        description='Retours à domicile',
        disabled=False,
        indent=False
    )
    dc_cumul = widgets.Checkbox(
        value=False,
        description='Nombre cumulé de personnes décédées',
        disabled=False,
        indent=False
    )
    dc_non_cumul = widgets.Checkbox(
        value=True,
        description='Nombre de décès par jour',
        disabled=False,
        indent=False
    )
    
    return hosp,rea,rad,dc_cumul,dc_non_cumul

## Plot data
def plotData(hosp,rea,rad,dc_cumul,dc_non_cumul):
    if hosp or rea or rad or dc_cumul:
        fig, ax1 = plt.subplots(figsize=figsize)
        if hosp:
            data_sum['hosp'].plot(legend=legend,color='blue')
            plt.annotate('Max hosp='+str(data_sum['hosp'].max()),xy=(str(data_sum['hosp'].argmax())[:10],data_sum['hosp'].max()),ha=ha)
        if rea:
            data_sum['rea'].plot(legend=legend,color='red')
            plt.annotate('Max rea='+str(data_sum['rea'].max()),xy=(str(data_sum['rea'].argmax())[:10],data_sum['rea'].max()),ha=ha)
        if rad:
            data_sum['rad'].plot(legend=legend,color='green')
        if dc_cumul:
            data_sum['dc_cumul'].plot(legend=legend,color='black',style='--')

        plt.title('Données hospitalières de la COVID-19 du '+str(min(data_sum.index))[:10]+' au '+str(max(data_sum.index))[:10]+' | France',
                  fontsize=fontsize,fontweight=fontweight,pad=15)
        plt.xlabel('Mois-Jour')
        plt.ylabel('Nombre de cas')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(format_date[3:])) 
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_interval)) 
        plt.gcf().autofmt_xdate()

        if hosp and rea and rad and dc_cumul:
            plt.yticks(np.arange(0,max(data_sum.max())+1,y_interval*2))
        else:
            plt.yticks(np.arange(0,max(data_sum[['hosp','rea','dc_cumul']].max())+1,y_interval))

        plt.gca().yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
        plt.annotate('Confinement 1',xy=('2020-04-13', 0),ha=ha,xytext=(0, 10),textcoords=textcoords)
        plt.annotate('',xy=('2020-03-18', 0),xytext=('2020-05-10', 0),arrowprops=arrowprops)

        plt.annotate('Couvre feu', xy=('2020-10-23', 0),ha=ha,xytext=(0, -10),textcoords=textcoords)
        plt.annotate('',xy=('2020-10-17', 0),xytext=('2020-10-29', 0),arrowprops=arrowprops)

        plt.annotate('Confinement 2',xy=('2020-11-05', 0),ha=ha,xytext=(0, 10),textcoords=textcoords)
        plt.annotate('',xy=('2020-10-29', 0),xytext=(str(max(data_sum.index))[:10], 0),arrowprops=arrowprops)

        if dc_non_cumul:
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            data_sum['dc_non_cumul'].plot(legend=legend,color='black')
            ax2.set_ylabel('Nombre de décès par jour')
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(format_date[3:])) 
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_interval)) 
            plt.gcf().autofmt_xdate()
            plt.annotate('Max dc_non_cumul='+str(data_sum['dc_non_cumul'].max()),xy=(str(data_sum['dc_non_cumul'].argmax())[:10],data_sum['dc_non_cumul'].max()),
                         ha=ha,xytext=(str(data_sum['dc_non_cumul'].argmax())[:10],data_sum['dc_non_cumul'].max()+20))

        fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
        plt.rc('xtick',labelsize=labelsize)
        plt.rc('ytick',labelsize=labelsize)
        plt.show()
