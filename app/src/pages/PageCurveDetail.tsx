import React, { useState, useEffect, useRef } from 'react';
import { useTranslation, setDefaults } from 'react-i18next';
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons, IonLabel, IonButton, IonIcon, IonGrid, IonCard, IonCardContent, IonList, IonAlert, IonItem, IonNote, IonRefresher, IonRefresherContent, useIonViewWillEnter } from '@ionic/react';
import { RouteComponentProps, useHistory } from 'react-router';
import { chevronBack, sunny  } from 'ionicons/icons';
import { Chart, ICurve, IChange, IOnChange } from 'src/components/Chart';
import { ChartModal } from '../components/ChartModal';
import { useApi } from '../components/useApi';
import { Range } from '../components/Range';
import { HapticsImpactStyle, useHaptics } from '../components/useHaptics';
import { debounce } from 'lodash';
import { ListFooter } from 'src/components/ListFooter';
import { CurveTypeBadge } from './PageCurves';
import { RefresherEventDetail } from '@ionic/core';

interface ICurveDetailProps extends RouteComponentProps<{
  id: string;
}> {}

const PageCurveDetail : React.FC<ICurveDetailProps> = ({match}) => {
  const pageRef = useRef();

  const [curve, setCurve] = useState<ICurve>()
  const [isModalOpen, setModalOpen] = useState(false);
  const [showDeleteAlert, setShowDeleteAlert] = useState(false);
  const [showRenameAlert, setShowRenameAlert] = useState(false);
  const { t } = useTranslation(['common', 'curves']);
  const api = useApi();
  let history = useHistory();

  const [ Haptics ] = useHaptics();

  useEffect(()=>{
    update()
  }, [])

  const update = () => (
    api.get({url: `/curves/${match.params.id}`}).then(data=>{
      setCurve(data)
    })
  )

  const doRefresh = (e: CustomEvent<RefresherEventDetail>) => {
    update().then(()=>e.detail.complete())
  }

  const handlePointChange = (change: IChange) => {
    api.put({
      url: `/curves/${curve?.id}/${change.index}`,
      data: {x: change.x, y: change.y}
    }).then(data=>{
      setCurve(data)
    })
  }

  const handlePointInsert = (itemIndex: number, position: 'before'|'after') => {
    api.post({
      url: `/curves/${curve?.id}/${itemIndex}`,
      data: {position: position}
    }).then(data=>{
      setCurve(data)
    })
  }

  const handlePointDelete = (itemIndex: number) => {
    api.delete({
      url: `/curves/${curve?.id}/${itemIndex}`
    }).then(data=>{
      setCurve(data)
    })
  }

  const onChange: IOnChange = {
    change: handlePointChange, 
    insert: handlePointInsert, 
    delete: handlePointDelete
  }


  const handleModalOpen = () => {
    Haptics.impact({style: HapticsImpactStyle.Medium})
    setModalOpen(true)
  }

  const handleOffsetChange = debounce((change: number) => {
    api.put({
      url: `/curves/${curve?.id}`,
      data: {offset: change}
    }).then(data=>{
      setCurve(data)
    })
  }, 500);

  if (!curve) {
    return null;
  } else {
    const name = curve.default?t(`curves:default_names.${curve.kind}`):curve.name
    return (
      <IonPage ref={pageRef}>
        <IonHeader translucent>
          <IonToolbar>
            <IonButtons slot="start">
              <IonButton routerLink='/curves' routerDirection='back'>
                <IonIcon slot='start' icon={chevronBack} />
                {t('curves:title')}
              </IonButton>
            </IonButtons>
            <IonTitle>{name}</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonContent fullscreen>
          <IonRefresher slot="fixed" onIonRefresh={doRefresh}>
            <IonRefresherContent/>
          </IonRefresher>
          <IonGrid fixed>
            <IonHeader collapse="condense">
              <IonToolbar>
                <IonTitle size="large">{name}</IonTitle>
              </IonToolbar>
            </IonHeader>
            <IonList inset>
              <IonItem button onClick={()=>setShowRenameAlert(true)}>
                <IonLabel>{t('curves:create.name')}</IonLabel>
                <IonNote>{curve.name}</IonNote>
              </IonItem>
              <IonItem>
                <IonLabel>{t('curves:create.type')}</IonLabel>
                <CurveTypeBadge curve={curve}/>
              </IonItem>
            </IonList>
            <IonCard onClick={handleModalOpen}>
              <IonCardContent>
                <Chart curve={curve} onChange={onChange}/>
              </IonCardContent>
              <ChartModal isOpen={isModalOpen} onClose={()=>setModalOpen(false)} pageRef={pageRef.current} title={name}>
                <Chart curve={curve} onChange={onChange} />
              </ChartModal>
            </IonCard>
            <IonList inset className='lp-remove-margin-bottom'>
              <Range min={-250} max={250} step={5} snaps ticks={false} label={t('curves:offset')} reset onChange={handleOffsetChange} defaultValue={curve.offset}>
                <IonIcon size='small' slot='start' icon={sunny} onClick={()=>handleOffsetChange(curve.offset-5)}/>
                <IonIcon slot='end' icon={sunny} onClick={()=>handleOffsetChange(curve.offset+5)}/>
              </Range>
            </IonList>
            <ListFooter>
              <IonLabel>{t('curves:descriptions.offset')}</IonLabel>
            </ListFooter>
            {!curve.default?
            <IonButton onClick={()=>setShowDeleteAlert(true)} className='inset' expand='block' color='danger'>
              {t('common:actions.delete')}
            </IonButton>
            :undefined}
            <IonAlert
              isOpen={showDeleteAlert}
              onDidDismiss={() => setShowDeleteAlert(false)}
              header={t('curves:delete.title', {name: curve.name})}
              message={t('curves:delete.text', {name: curve.name})}
              buttons={[
                {
                  text: t('common:actions.cancel'),
                  role: 'cancel',
                  cssClass: 'secondary',
                  handler: () => setShowDeleteAlert(false)
                },
                {
                  text: t('common:actions.delete'),
                  role: 'delete',
                  handler: () => {
                    api.delete({url: `/curves/${curve.id}`}).then(()=>{
                      history.push('/curves')
                    })
                  }
                }
              ]}
            />
            <IonAlert
              isOpen={showRenameAlert}
              onDidDismiss={() => setShowRenameAlert(false)}
              header={t('curves:rename.title', {name: curve.name})}
              buttons={[
                {
                  text: t('common:actions.cancel'),
                  role: 'cancel',
                  cssClass: 'secondary',
                  handler: () => setShowRenameAlert(false)
                },
                {
                  text: t('common:actions.done'),
                  handler: (data) => {
                    api.put({
                      url: `/curves/${curve.id}`,
                      data: {name: data.name}
                    }).then(data=>setCurve(data))
                  }
                }
              ]}
              inputs={[
                {
                  name: 'name',
                  type: 'text',
                  id: 'name-id',
                  value: curve.name,
                  placeholder: ''
                }
              ]}
            />
          </IonGrid>
        </IonContent>
      </IonPage>
    )
  }
}

export default PageCurveDetail;


