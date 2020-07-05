import  React from 'react';
import { IonList, IonItem, IonLabel, IonIcon } from '@ionic/react';
import { IGroup } from '../types/hue';
import Room from '../icons/room.svg';
import Zone from '../icons/zone.svg';
import { ListHeader } from './ListHeader';
import { useTranslation } from 'react-i18next';

interface IGroupListProps {
  groups: IGroup[];
}
export const GroupList: React.FC<IGroupListProps> = ({groups}) => {
  const { t } = useTranslation('groups');
  const icon = (group: IGroup) => {
    if (group.type === 'Room') {
      return <IonIcon slot='start' src={Room} className='lp-icon-fill' style={{backgroundColor: 'var(--apple-system-orange)'}}/> 
    } else if (group.type === 'Zone') {
      return <IonIcon slot='start' src={Zone} className='lp-icon-fill' style={{backgroundColor: 'var(--apple-system-pink)'}} /> 
    } else {
      return undefined
    }
  }
  const rooms = groups.filter(group=>group.type==='Room').map((group, index) => (
    <IonItem button routerLink={`/groups/${group.id}`} routerDirection='forward' key={index}>
      <IonLabel>{group.name}</IonLabel>
      {icon(group)}
    </IonItem>
  ))
  const zones = groups.filter(group=>group.type==='Zone').map((group, index) => (
    <IonItem button routerLink={`/groups/${group.id}`} routerDirection='forward' key={index}>
      <IonLabel>{group.name}</IonLabel>
      {icon(group)}
    </IonItem>
  ))
  return (
    <div>
      <ListHeader inset>
        <IonLabel>{t('zones')}</IonLabel>
      </ListHeader>
      <IonList inset>
        {zones}
      </IonList>
      <ListHeader inset>
        <IonLabel>{t('rooms')}</IonLabel>
      </ListHeader>
      <IonList inset>
        {rooms}
      </IonList>
    </div>
  )
}
