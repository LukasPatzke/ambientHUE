import React, { useRef, useState, useEffect } from 'react';
import { IonModal, IonHeader, IonToolbar, IonTitle, IonSlides, IonSlide, IonContent, IonButton, IonList, IonItem, IonLabel, IonNote, IonIcon, IonInput, IonSpinner, IonItemDivider, IonFooter } from '@ionic/react';
import { Content } from './Content';
import { IBridgeDiscovery, IBridgeSync } from 'src/types/hue';
import { useApi } from './useApi';
import  devicesBridgesV2 from '../icons/hue/devicesBridgesV2.svg';
import { ListHeader } from './ListHeader';
import { SpinnerCircularSplit } from 'spinners-react';
import { useTranslation } from 'react-i18next';

interface IHueConfigProps {
  isOpen: boolean
  onAbbort: ()=>void
  onFinish: ()=>void
}

type state = 'loading'|'success'|'failure'

export const HueConfig: React.FC<IHueConfigProps> = ({isOpen, onAbbort, onFinish}) => {
  const slidesRef = useRef<HTMLIonSlidesElement>(null);
  const inputRef = useRef<HTMLIonInputElement>(null)

  const [discovered, setDiscovered] = useState<IBridgeDiscovery[]>([])
  const [connectionState, setConnectionState] = useState<state>('loading')
  const [result, setResult] = useState<IBridgeSync>()

  const { get, post } = useApi();
  const { t } = useTranslation(['common', 'settings']);

  useEffect(()=>{
    get({url: '/bridge/discover'}).then(data=>setDiscovered(data))
  }, [])

  const next = () => {
    slidesRef.current?.lockSwipeToNext(false);
    slidesRef.current?.slideNext();
    slidesRef.current?.lockSwipeToNext(true);
  }

  const prev = () => {
    slidesRef.current?.lockSwipeToPrev(false);
    slidesRef.current?.slidePrev();
    slidesRef.current?.lockSwipeToPrev(true);
    setConnectionState('loading')
  }

  const submit = (ipaddress: string) => {
    next()
    post({
      url: '/bridge/',
      data: {ipaddress: ipaddress}
    }).then(data=>{
      setResult(data)
      setConnectionState('success')
    }).catch(error=>{
      setConnectionState('failure')
    })
  }

  const discoveredBridges = discovered.map((item, index)=>(
    <IonItem key={index} button onClick={()=>submit(item.internalipaddress)}>
      <IonIcon color='primary' slot='start' icon={devicesBridgesV2}/> 
      <IonLabel>
        {item.name||'Hue Bridge'}
        <IonNote>{item.internalipaddress}</IonNote>
      </IonLabel>
    </IonItem>
  ))

  return (
    <IonModal isOpen={isOpen}>
      <IonContent>
      <IonSlides ref={slidesRef} options={{allowSlidePrev: false, allowSlideNext: false, initialSlide: 0}}>
        <IonSlide>
          <Content>
            <div style={{height: '40px'}}/>
            <h1>{t('settings:init.1.title')}</h1>
            <IonItemDivider/>
            <ListHeader>
              <IonLabel>{t('settings:init.1.autoconfig')}</IonLabel>
            </ListHeader>
            <IonList>
              {discoveredBridges}
            </IonList>
            <div style={{height: '1.5em'}}/>
            <ListHeader>
              <IonLabel>{t('settings:init.1.manualconfig')}</IonLabel>
            </ListHeader>
            <IonList>
              <IonItem>
                <IonLabel>IP Address</IonLabel>
                <IonInput ref={inputRef} placeholder='192.168.178.23'/>
                <IonButton 
                  slot='end'
                  fill='clear'
                  size='default'
                  onClick={()=>{if(inputRef.current?.value) {submit(inputRef.current?.value as string)}}}
                >
                  {t('common:actions.next')}
                </IonButton>
              </IonItem>
            </IonList>
            <div style={{height: '1.5em'}}/>
          </Content>
        </IonSlide>
        <IonSlide>
          <Content>
            <div style={{height: '40px'}}/>
            <h1 style={{minHeight: '2.4em'}}>{t(`settings:init.2.${connectionState}`)}</h1>
            <Icon state={connectionState}/>
            <div style={{height: '3em'}}>
              <IonLabel>
                {connectionState==='success'?t('settings:init.2.found', result):undefined}
              </IonLabel>
            </div>
            {connectionState==='loading'?<IonButton onClick={prev} color='medium'>{t('common:actions.cancel')}</IonButton>:undefined}
            {connectionState==='success'?<IonButton onClick={onFinish} color='primary'>{t('common:actions.done')}</IonButton>:undefined}
            {connectionState==='failure'?<IonButton onClick={prev} color='primary'>{t('common:actions.back')}</IonButton>:undefined}
          </Content>
        </IonSlide>
      </IonSlides>
      </IonContent>
    </IonModal>
  )
}



interface IIconProps {
  state: state
}

interface IOptions {
  ionColor: string
  color: string
  secondaryColor: string
  enabled: boolean
}

const Icon: React.FC<IIconProps> = ({state}) => {
  var options: IOptions;
  if (state==='loading') {
    options = {
      ionColor: 'primary',
      color: '#3880ff',
      secondaryColor: '#f4f5f8',
      enabled: true
    }
  } else if (state==='success') {
    options = {
      ionColor: 'success',
      color: '#2dd36f',
      secondaryColor: '#2dd36f',
      enabled: true
    }
  } else if (state==='failure') {
    options = {
      ionColor: 'danger',
      color: '#eb445a',
      secondaryColor: '#eb445a',
      enabled: true
    }
  } else {
    options = {
      ionColor: 'medium',
      color: '#92949c',
      secondaryColor: '#f4f5f8',
      enabled: true
    }
  }
  return (
    <div className='lp-spinner'>
      <IonIcon 
        color={options.ionColor}
        style={{fontSize: 140}} 
        icon={devicesBridgesV2}
      /> 
      <SpinnerCircularSplit 
        size={256} 
        thickness={75} 
        speed={50}
        color={options.color}
        secondaryColor={options.secondaryColor}
        enabled={options.enabled}
      />
    </div>
  )
}