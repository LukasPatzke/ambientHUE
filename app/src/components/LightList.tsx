import  React from 'react';
import { IonList, IonItem, IonLabel, IonIcon } from '@ionic/react';
import { bulb } from 'ionicons/icons';
import { ILight, ILightInfo } from '../types/hue';


export const isLightHueControlled = (light: ILightInfo|ILight) => {
  if (light.type==='Color light') {
    return true
  } else if (light.type==='Extended color light') {
    return true
  } else {
    return false
  }
}

export const isLightCtControlled = (light: ILightInfo|ILight) => {
  if (light.type==='Color temperature light') {
    return true
  } else if (light.type==='Extended color light') {
    return true
  } else {
    return false
  }
}

export const isLightBriControlled = (light: ILightInfo|ILight) => {
  if (light.type==='On/off light') {
    return false
  } else if (light.type==='On/Off plug-in unit') {
    return false
  } else {
    return true
  }
}

interface ILightListProps {
  lights: ILightInfo[];
}

export const LightList: React.FC<ILightListProps> = ({lights}) => {
  const icon = (light: ILightInfo) => {
    if (isLightHueControlled(light)) {
      return <IonIcon slot='start' icon={bulb} className='lp-icon-fill' style={{backgroundColor: 'var(--apple-system-purple)'}}/>
    } else if (isLightCtControlled(light)) {
      return <IonIcon slot='start' icon={bulb} className='lp-icon-fill' style={{backgroundColor: 'var(--apple-system-orange)'}}/>
    } else {
      return <IonIcon slot='start' icon={bulb} className='lp-icon-fill' style={{backgroundColor: 'var(--ion-color-dark)', color: 'var(--ion-color-light)'}}/>
    }
  }
  const items = lights.map((light, index) => (
    <IonItem routerLink={`/lights/${light.id}`} routerDirection='forward' key={index}>
      {icon(light)}
      <IonLabel>{light.name}</IonLabel>
    </IonItem>
  ))
  return (
    <IonList inset>
      {items}
    </IonList>
  )
}
