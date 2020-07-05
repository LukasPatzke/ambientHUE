import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons, IonButton, IonIcon, IonLabel, IonGrid, IonRefresher, IonRefresherContent } from '@ionic/react';
import { IGroup, ILightUpdate } from '../types/hue';
import { RouteComponentProps } from 'react-router';
import { chevronBack } from 'ionicons/icons';
import { LightSettings } from '../components/LightSettings';
import { ListHeader } from '../components/ListHeader';
import { LightList } from '../components/LightList';
import { useApi } from '../components/useApi';
import { RefresherEventDetail } from '@ionic/core';

interface IPageGroupDetail extends RouteComponentProps<{
  id: string;
}> {}

const PageGroupDetail : React.FC<IPageGroupDetail> = ({match}) => {
  const [group, setGroup] = useState<IGroup>()
  const { t } = useTranslation(['groups', 'lights']);
  const { get, put } = useApi();

  useEffect(()=>{
    update()
  }, [])

  const update = () => (
    get({url: `/groups/${match.params.id}`}).then(data=>{
      setGroup(data)
    })
  )

  const doRefresh = (e: CustomEvent<RefresherEventDetail>) => {
    update().then(()=>e.detail.complete())
  }

  const handleChange = (change: ILightUpdate) => {
    put({
      url: `/groups/${match.params.id}`,
      data: change
    }).then(data=>{
      setGroup(data)
    })
    }

  if (!group) {
    return null;
  } else {
    return (
      <IonPage>
        <IonHeader translucent>
          <IonToolbar>
            <IonButtons slot="start">
              <IonButton routerLink='/groups' routerDirection='back'>
                <IonIcon slot='start' icon={chevronBack} />
                {t('groups:title')}
              </IonButton>
            </IonButtons>
            <IonTitle>{group.name}</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonContent fullscreen>
          <IonRefresher slot="fixed" onIonRefresh={doRefresh}>
            <IonRefresherContent/>
          </IonRefresher>
          <IonGrid fixed>
          <IonHeader collapse="condense">
            <IonToolbar>
              <IonTitle size="large">{group.name}</IonTitle>
            </IonToolbar>
          </IonHeader>
            <ListHeader inset>
              <IonLabel>{t('lights:title')}</IonLabel>
            </ListHeader>
            <LightList lights={group.lights} />
            <ListHeader inset>
              <IonLabel>{t('lights:settings.title')}</IonLabel>
            </ListHeader>
            <LightSettings light={group.lights[0]} onChange={handleChange}/>
          </IonGrid>
        </IonContent>
      </IonPage>
    )
  }
}

export default PageGroupDetail;