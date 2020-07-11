import React, { useContext, useRef, useState, useEffect } from 'react';
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonGrid, IonItem, IonLabel, IonList, IonButtons, IonButton, IonIcon, IonNote, IonToggle, IonSegment, IonSegmentButton, IonModal, IonInput, IonTextarea, IonItemSliding, IonItemOptions, IonItemOption, IonRefresher, IonRefresherContent } from '@ionic/react';
import { IWebHook, method, trigger } from 'src/types/hue';
import { useApi } from 'src/components/useApi';
import { useTranslation } from 'react-i18next';
import { RouteComponentProps } from 'react-router';
import { chevronBack, add, addCircle } from 'ionicons/icons';
import { Content } from 'src/components/Content';
import { ListHeader } from 'src/components/ListHeader';
import { ListDivider } from 'src/components/ListDivider';
import { RefresherEventDetail } from '@ionic/core';

interface IModalState {
  isOpen: boolean
  isNew?: boolean
  webhook?: IWebHook
}
const PageWebhook: React.FC = () => {
  const [webhooks, setWebhooks] = useState<IWebHook[]>([])
  const [modalState, setModalState] = useState<IModalState>({isOpen: false, isNew: true, webhook: undefined})
  const api = useApi();
  const { t } = useTranslation(['common', 'webhooks'])

  const pageRef = useRef();
  const customsListRef = useRef<HTMLIonListElement>(null); 

  useEffect(()=>{
    update()
  }, [])

  const update = () => (api.get({url: '/webhooks/'}).then(data=>setWebhooks(data)))

  const handleDelete = (webhook: IWebHook) => {
    api.delete({
      url: `/webhooks/${webhook.id}`
    }).then(update).then(()=>{
      if (customsListRef.current) {
        customsListRef.current.closeSlidingItems()
      }
    })
  }

  const doRefresh = (e: CustomEvent<RefresherEventDetail>) => {
    update().then(()=>e.detail.complete())
  }

  const items = webhooks.map((webhook, index)=>(
    <IonItemSliding key={index}>
      <IonItem key={index} button onClick={()=>setModalState({isOpen: true, isNew: false, webhook: webhook})}>
        <IonLabel>{webhook.name}</IonLabel>
      </IonItem>
      <IonItemOptions slot='end'>
        <IonItemOption onClick={()=>handleDelete(webhook)} color='danger'>{t('common:actions.delete')}</IonItemOption>
      </IonItemOptions>
    </IonItemSliding>
  ))

  return (
    <IonPage ref={pageRef}>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonButton routerLink='/settings' routerDirection='back'>
              <IonIcon slot='start' icon={chevronBack} />
              {t('settings:title')}
            </IonButton>
          </IonButtons>
          <IonTitle>{t('webhooks:title')}</IonTitle>
          <IonButtons slot="end">
            <IonButton onClick={()=>setModalState({isOpen: true, isNew: true})} >
              <IonIcon slot='icon-only' icon={add} />
            </IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonRefresher slot="fixed" onIonRefresh={doRefresh}>
          <IonRefresherContent/>
        </IonRefresher>
        <IonGrid fixed>
        <IonHeader collapse='condense'>
          <IonToolbar>
            <IonTitle size='large'>{t('webhooks:title')}</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonList ref={customsListRef} inset>
          {items}
        </IonList>
        <IonButton className='inset primary translucent' expand='block' onClick={()=>setModalState({isOpen: true, isNew: true})} >
        <IonIcon slot='start' icon={addCircle} color='primary'/>
      <IonLabel color='primary'>{t('common:actions.add')}</IonLabel>
        </IonButton>
        </IonGrid>
      </IonContent>
      <WebhookModal 
        {...modalState} 
        onChange={()=>update().then(()=>setModalState({isOpen: false}))}
        onClose={()=>setModalState({isOpen: false})} 
        pageRef={pageRef.current}
      />
    </IonPage>
  )
}

export default PageWebhook

interface IWebhookModalProps {
  isOpen: boolean;
  onClose: ()=>void;
  onChange: ()=>void;
  pageRef?: HTMLElement;
  webhook?: IWebHook;
  isNew?: boolean
}

const WebhookModal: React.FC<IWebhookModalProps> = ({isOpen, onClose, onChange, pageRef, webhook=({body: '{}', method:'GET', trigger:'status', on:true} as IWebHook), isNew}) => {
  const { t, } = useTranslation(['common', 'webhooks']);

  const { post, put } = useApi()

  const save = () => {
    if (webhook.id) {
      put({
        url: `/webhooks/${webhook.id}`,
        data: webhook
      }).then(onChange)
    } else {
      post({
        url: `/webhooks/`,
        data: webhook
      }).then(onChange)
    }
  }

  return (
    <IonModal isOpen={isOpen} presentingElement={pageRef} swipeToClose onDidDismiss={onClose}>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot='start'>
            <IonButton onClick={onClose}>{t('common:actions.cancel')}</IonButton>
          </IonButtons>
          <IonTitle>{t(isNew?'webhooks:create':'webhooks:edit')}</IonTitle>
          <IonButtons slot='end'>
            <IonButton onClick={save}>{t('common:actions.done')}</IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <Content>
        <ListDivider/>
        <IonList lines='inset' >
          <IonItem>
            <IonLabel>{t('webhooks:name')}</IonLabel>
            <IonInput value={webhook.name} placeholder={t('webhooks:name')} onIonChange={(e)=>webhook.name = String(e.detail.value)} />
          </IonItem>
          <IonItem>
            <IonLabel>{t('webhooks:on')}</IonLabel>
            <IonToggle checked={webhook.on} onIonChange={(e)=>webhook.on = e.detail.checked} />
          </IonItem>
        </IonList>
        <ListDivider/>
        <IonList>
          <IonItem>
            <IonLabel>{t('webhooks:url')}</IonLabel>
            <IonInput inputMode='url' value={webhook.url} placeholder='http://example.com/path' onIonChange={(e)=>webhook.url = String(e.detail.value)} />
          </IonItem>
          <IonItem>
            <IonLabel>{t('webhooks:method')}</IonLabel>
            <IonSegment color='primary' value={webhook.method} onIonChange={(e)=>webhook.method=e.detail.value as method}>
              <IonSegmentButton value='GET'>GET</IonSegmentButton>
              <IonSegmentButton value='POST'>POST</IonSegmentButton>
            </IonSegment>
          </IonItem>
          <IonItem>
            <IonLabel>{t('webhooks:trigger')}</IonLabel>
            <IonSegment color='primary' value={webhook.trigger} onIonChange={(e)=>webhook.trigger=e.detail.value as trigger}>
              <IonSegmentButton value='status'>{t('webhooks:trigger_status')}</IonSegmentButton>
              <IonSegmentButton value='lights'>{t('webhooks:trigger_lights')}</IonSegmentButton>
              <IonSegmentButton value='groups'>{t('webhooks:trigger_groups')}</IonSegmentButton>
            </IonSegment>
          </IonItem>
        </IonList>
        <ListHeader><IonLabel>{t('webhooks:body')}</IonLabel></ListHeader>
        <IonList>
          <IonItem>
            <IonTextarea value={webhook.body} onIonChange={(e)=>webhook.body = String(e.detail.value)} />
          </IonItem>
        </IonList>
      </Content>
    </IonModal>
  )
}



interface IWebhookDetailProps extends RouteComponentProps<{
  id: string;
}> {}

export const PageWebhookDetail: React.FC<IWebhookDetailProps> = ({match}) => {
  const [webhook, setWebhook] = useState<IWebHook>()
  const { get, put } = useApi();
  const { t } = useTranslation(['common', 'webhook'])

  const pageRef = useRef();

  useEffect(()=>{
    get({url: `/webhook/${match.params.id}`}).then(data=>setWebhook(data))
  })

  const setMethod = (method: method) => {

  }

  return (
    <IonPage ref={pageRef}>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonButton routerLink='/settings/webhooks' routerDirection='back'>
              <IonIcon slot='start' icon={chevronBack} />
              {t('webhooks:title')}
            </IonButton>
          </IonButtons>
          <IonTitle>{webhook?.name}</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonGrid fixed>
        <IonHeader collapse='condense'>
          <IonToolbar>
            <IonTitle size='large'>{webhook?.name}</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonList>
          <IonItem>
            <IonLabel>{t('webhooks:name')}</IonLabel>
            <IonNote>{webhook?.name}</IonNote>
          </IonItem>
          <IonItem>
            <IonLabel>{t('webhooks:on')}</IonLabel>
            <IonToggle 
              checked={webhook?.on} 
              onIonChange={(e)=>put({url: `/webhook/${match.params.id}`, data:{on: e.detail.checked}}).then(data=>setWebhook(data))} />
          </IonItem>
        </IonList>
        <IonList>
          <IonItem>
            <IonLabel>{t('webhooks:url')}</IonLabel>
            <IonNote>{webhook?.url}</IonNote>
          </IonItem>
          <IonItem>
            <IonLabel>{t('webhooks:method')}</IonLabel>
            <IonSegment color='primary' value={webhook?.method} onIonChange={(e)=>setMethod(e.detail.value as method)}>
              <IonSegmentButton value='GET'>GET</IonSegmentButton>
              <IonSegmentButton value='POST'>POST</IonSegmentButton>
            </IonSegment>
          </IonItem>
        </IonList>
        </IonGrid>
      </IonContent>
    </IonPage>
  )
}