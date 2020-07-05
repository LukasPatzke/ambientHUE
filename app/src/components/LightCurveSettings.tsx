import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {  IonList, IonLabel, IonIcon, IonItem, IonToggle, IonNote, IonModal, IonHeader, IonToolbar, IonTitle, IonButtons, IonButton, IonBadge } from '@ionic/react';
import { Range } from './Range';
import { debounce } from 'lodash';
import { ILight, ILightUpdate, ICurve } from '../types/hue';
import { sunny, add, remove, checkmark } from 'ionicons/icons';
import { isLightCtControlled, isLightBriControlled } from './LightList';
import { Content } from './Content';
import { useApi } from './useApi';


interface ILightCurveSettingsProps {
  light: ILight;
  onChange: (change: ILightUpdate) => void;
  pageRef?: HTMLElement;
}

export const LightCurveSettings: React.FC<ILightCurveSettingsProps> = ({light, onChange, pageRef}) => {
  const [isCtModalOpen, setCtModalOpen] = useState(false);
  const [isBriModalOpen, setBriModalOpen] = useState(false);

  const { t } = useTranslation('curves');
  const onBrightnessMaxChange = debounce((value:number)=>(
    onChange({bri_max: value} as ILightUpdate)), 250);
  const onThresholdChange = debounce((value:number)=>(
    onChange({on_threshold: value} as ILightUpdate)), 250);

  if (!isLightCtControlled(light) && !isLightBriControlled(light)) {
    return null
  }
  
  return (
    <IonList inset>
      {isLightBriControlled(light)?
      <IonItem button onClick={()=>setBriModalOpen(true)}>
        <IonLabel>{t('default_names.bri')}</IonLabel>
        <IonNote>{light.bri_curve.name}</IonNote>
      </IonItem>
      :undefined}
      {isLightCtControlled(light)?
      <IonItem button onClick={()=>setCtModalOpen(true)}>
        <IonLabel>{t('default_names.ct')}</IonLabel>
        <IonNote>{light.ct_curve.name}</IonNote>
      </IonItem>
      :undefined}
      <CurveSettings 
        isOpen={isCtModalOpen}
        kind='ct'
        defaultValue={light.ct_curve}
        onClose={()=>setCtModalOpen(false)}
        onSelect={(change)=>{onChange(change);setCtModalOpen(false)}}
        pageRef={pageRef}
      />
      <CurveSettings 
        isOpen={isBriModalOpen}
        kind='bri'
        defaultValue={light.bri_curve}
        onClose={()=>setBriModalOpen(false)}
        onSelect={(change)=>{onChange(change);setBriModalOpen(false)}}
        pageRef={pageRef}
      />
    </IonList>
  )
}


interface ICurveSettingsProps {
  isOpen: boolean;
  kind: 'bri'|'ct';
  defaultValue: ICurve;
  onClose: ()=>void;
  onSelect: (change: ILightUpdate) => void;
  pageRef?: HTMLElement;
}

const CurveSettings: React.FC<ICurveSettingsProps> = ({isOpen, kind, defaultValue, onClose, onSelect, pageRef}) => {
  const { t, i18n } = useTranslation(['common', 'curves']);
  const [curves, setCurves] = useState<ICurve[]>([]);

  const { get } = useApi();

  useEffect(()=>{
    get({url: `/curves/?kind=${kind}`}).then(data=>{
      setCurves(data)
    })
  }, [])

  const curveItems = curves.map((curve, index)=>(
    <IonItem 
      key={index} button detailIcon='none' 
      onClick={()=>{
        if (kind==='bri') {
          onSelect({bri_curve_id: curve.id})
        } else if (kind==='ct') {
          onSelect({ct_curve_id: curve.id})
        }
      }}
    >
      <IonLabel>{curve.name}</IonLabel>
      {curve.default?<IonBadge color='medium'>default</IonBadge>:undefined}
      {curve.id===defaultValue.id?<IonIcon slot='end' color='primary' icon={checkmark} />:undefined}
    </IonItem>
  ))
  return (
    <IonModal isOpen={isOpen} presentingElement={pageRef} swipeToClose onDidDismiss={onClose}>
      <IonHeader>
        <IonToolbar>
          <IonTitle>{t('curves:title')}</IonTitle>
          <IonButtons slot='end'>
            <IonButton onClick={onClose}>{t('common:actions.cancel')}</IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <Content>
        <IonList lines='inset' >
          {curveItems}
        </IonList>
      </Content>
    </IonModal>
  )
}