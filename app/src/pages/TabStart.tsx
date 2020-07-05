import React, { useRef, useState, useEffect, RefObject } from 'react';
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonGrid, IonCard, IonCardContent, IonIcon, IonLabel, IonRow, IonCol, IonButtons, IonButton, IonModal, IonReorderGroup, IonItem, IonReorder, IonList, IonRefresher, IonRefresherContent, IonItemSliding, IonItemOptions, IonItemOption, useIonViewWillEnter } from '@ionic/react';
import { ItemReorderEventDetail, RefresherEventDetail } from '@ionic/core';
import './TabStart.css';
import { IPosition } from 'src/types/hue';
import { useApi } from '../components/useApi';
import appIcon from '../icons/icon.svg'
import appIconColor from '../icons/icon-color.svg'
import { bulb, grid, addCircle, removeCircle } from 'ionicons/icons';
import { useTranslation } from 'react-i18next';
import { ListHeader } from 'src/components/ListHeader';
import { position as dummyPosition } from '../dummies';




const TabStart: React.FC = () => {
  const pageRef = useRef();
  const [positions, setPositions] = useState<IPosition[]>([dummyPosition, dummyPosition, dummyPosition])
  const [active, setActive] = useState<boolean>(false);
  const [reorder, setReorder] = useState<boolean>(false)
  const { get, put } = useApi();

  const { t } = useTranslation('common')

  useIonViewWillEnter(()=>{
    update()
  })

  const update = ()=>([
    get({url: '/positions/'}).then(data=>setPositions(data)),
    get({url: '/status/'}).then(data=>setActive(data.status))
  ])

  const doRefresh = (e: CustomEvent<RefresherEventDetail>) => {
    Promise.all(update()).then(()=>e.detail.complete())
  }

  const handleVisible = (id: number, visible:boolean) => (
    put({
      url: `/positions/${id}`,
      data: {visible: visible}
    }).then(data=>{
      setPositions(data)
    })
  )

  const handleReorder = (event: CustomEvent<ItemReorderEventDetail>) => {
    put({
      url: '/positions/',
      data: {move_from: event.detail.from, move_to: event.detail.to}
    }).then(data=>{
      event.detail.complete(positions)
      setPositions(data)
    })
  }
  
  const tiles = positions.filter(pos=>pos.visible).map((pos, index)=>{
      if (pos.light) {
        return (
          <Tile
            key={index}
            icon={bulb}
            label={pos.light.name}
            state={pos.light.on}
            routerLink={`/lights/${pos.light.id}`}
            disabled={!active}
          />
        )
      } else if (pos.group) {
        return (
          <Tile
            key={index}
            icon={grid}
            label={pos.group.name}
            state={pos.group.lights[0]?.on}
            routerLink={`/groups/${pos.group.id}`}
            disabled={!active}
          />
        )
      }
    })
  return (
    <IonPage ref={pageRef}>
      <IonHeader translucent>
        <IonToolbar>
          <IonButtons slot="end">
            <IonButton onClick={()=>setReorder(true)} >
              {t('actions.edit')}
            </IonButton>
          </IonButtons>
          <IonTitle>Hue Dimmer</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonRefresher slot="fixed" onIonRefresh={doRefresh}>
          <IonRefresherContent/>
        </IonRefresher>
        <IonGrid fixed>
        <IonHeader collapse="condense">
          <IonToolbar>
            <IonTitle size="large">Hue Dimmer</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonRow class="ion-justify-content-start" style={{marginTop: '10px'}}>
          <Tile 
            icon={active?appIconColor:appIcon} 
            label='Hue Dimmer' 
            state={active} 
            size='large'
            onClick={()=>put({url: '/status/', data: {status: !active}}).then(data=>{
              setActive(data.status)
            })}
          />
        </IonRow>
        <ListHeader><IonLabel>Favoriten</IonLabel></ListHeader>
        <IonRow class="ion-justify-content-start">
          {tiles}
        </IonRow>
        </IonGrid>
      </IonContent>
      <ReorderModal 
        isOpen={reorder} 
        pageRef={pageRef.current} 
        positions={positions}
        onClose={()=>setReorder(false)}
        onVisible={handleVisible}
        onReorder={handleReorder}
      />
    </IonPage>
  );
};

interface ITile {
  icon: string
  label: string
  state: boolean
  onClick?: (event: React.MouseEvent<HTMLIonCardElement, MouseEvent>) => void
  routerLink?: string
  size?: 'small'|'large'
  style?: React.CSSProperties
  disabled?: boolean
}

export const Tile: React.FC<ITile> = ({icon, label, state, onClick, routerLink, size='small', style, disabled}) => {
  const colSize = size==='large'?'12':'auto';
  return (
    <IonCol sizeXl={colSize} sizeLg={colSize} sizeMd={colSize} sizeSm={colSize} sizeXs={size==='small'?'4':'12'}>
      <IonCard 
        onClick={onClick} 
        routerLink={routerLink} 
        disabled={disabled}
        style={style}  
        routerDirection='forward' 
        button
        className={size==='small'?'lp-tile':'lp-tile large'}
      >
        <IonCardContent className={disabled?'lp-tile-content disabled':'lp-tile-content'}>
          <div className='lp-tile-icon'><IonIcon icon={icon}/></div>
          <div className='lp-tile-text'>
            <div className='lp-tile-label'><IonLabel color={state?'dark':undefined}>{label}</IonLabel></div>
            <div className='lp-tile-state'><IonLabel>{state?'Ein':'Aus'}</IonLabel></div>
          </div>
        </IonCardContent>
      </IonCard>
    </IonCol>
  )
}

interface IReorderModal {
  isOpen: boolean
  onClose: ()=>void;
  pageRef?: HTMLElement;
  positions: IPosition[];
  onVisible: (id:number, visible:boolean)=>Promise<void>;
  onReorder: (event: CustomEvent<ItemReorderEventDetail>)=>void
}

const ReorderModal: React.FC<IReorderModal> = ({isOpen, onClose, pageRef, positions, onVisible, onReorder}) => {
  const { t } = useTranslation('common')
  let refs: RefObject<HTMLIonItemSlidingElement>[] = []
  positions.forEach(pos=>{refs.push(React.createRef<HTMLIonItemSlidingElement>())})
  
  // const itemRef = useRef(refs);

  const items = positions.map((pos, index)=>(
    <IonItemSliding key={index} ref={refs[index]}>
      <IonItemOptions 
        side='end'
        onIonSwipe={()=>{
          onVisible(pos.id, false)
          refs[index].current?.close()
        }}
      >
        <IonItemOption 
          onClick={()=>{
            onVisible(pos.id, false)
            refs[index].current?.close()
          }}
          expandable
          disabled={!pos.visible}
          color='danger'
        >
          {t('common:actions.hide')}
        </IonItemOption>
      </IonItemOptions>
      <IonItemOptions 
        side='start' 
        onIonSwipe={()=>{
          onVisible(pos.id, true)
          refs[index].current?.close()
        }}
      >
        <IonItemOption 
          onClick={()=>{
            onVisible(pos.id, true)
            refs[index].current?.close()
          }}
          expandable={!pos.visible}
          disabled={pos.visible}
          color='primary'
        >
          {t('common:actions.add')}
        </IonItemOption>
      </IonItemOptions>
      <IonItem key={index}>
        <IonButton 
          slot='start' fill='clear' 
          onClick={()=>{
            if ((pos.visible) && (refs[index].current)) {
              refs[index].current?.open('end')
            } else {
              onVisible(pos.id, !pos.visible)
            }
          }}
        >
          <IonIcon 
            slot='icon-only' 
            icon={pos.visible?removeCircle:addCircle}
            color={pos.visible?'danger':'success'}
          />
        </IonButton>
        <IonLabel>{pos.light?.name||pos.group?.name}</IonLabel>
        <IonReorder slot='end'/>
      </IonItem>
    </IonItemSliding>
    
  ))

  return (
    <IonModal presentingElement={pageRef} swipeToClose onDidDismiss={onClose} isOpen={isOpen}>
      <IonHeader>
          <IonToolbar>
            <IonTitle>{t('actions.reorder')}</IonTitle>
            <IonButtons slot='end'>
              <IonButton onClick={onClose}>{t('actions.done')}</IonButton>
            </IonButtons>
          </IonToolbar>
        </IonHeader>
        <IonContent>
          <IonList inset>
          <IonReorderGroup onIonItemReorder={onReorder} inlist disabled={false}>
            {items}
          </IonReorderGroup>
          </IonList>
        </IonContent>
    </IonModal>
  )
}

export default TabStart;
