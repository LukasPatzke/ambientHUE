import { IonApp, IonIcon, IonLabel, IonModal, IonRouterOutlet, IonTabBar, IonTabButton, IonTabs, IonToast, isPlatform } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
/* Core CSS required for Ionic components to work properly */
import '@ionic/react/css/core.css';
import '@ionic/react/css/display.css';
import '@ionic/react/css/flex-utils.css';
import '@ionic/react/css/float-elements.css';
/* Basic CSS for apps built with Ionic */
import '@ionic/react/css/normalize.css';
/* Optional CSS utils that can be commented out */
import '@ionic/react/css/padding.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/text-alignment.css';
import '@ionic/react/css/text-transformation.css';
import '@ionic/react/css/typography.css';
import { bulb, cog, grid, home } from 'ionicons/icons';
import React, { useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Redirect, Route } from 'react-router-dom';
import { InitialConfig } from './components/ServerConfig';
import { AppContext } from './components/State';
import icon from './icons/icon-transparent.png';
import PageGroupDetail from './pages/PageGroupDetail';
import PageGroups from './pages/PageGroups';
import PageLightDetail from './pages/PageLightDetail';
import PageLights from './pages/PageLights';
import TabSettings from './pages/TabSettings';
import TabStart from './pages/TabStart';
import PageCurves from './pages/PageCurves';
import PageCurveDetail from './pages/PageCurveDetail';
import * as serviceWorker from './serviceWorker';
import './theme/ui.css';
/* Theme variables */
import './theme/variables.css';
import appIcon from './icons/icon.svg';
import { HueConfig } from './components/HueConfig';
import { IBridge } from './types/hue';
import { useApi } from './components/useApi';


const App: React.FC = () => {
  const [serviceWorkerInitialized, setServiceWorkerInitialized] = useState(false);
  const [serviceWorkerUpdated, setServiceWorkerUpdated] = useState(false);
  const [serviceWorkerRegistration, setServiceWorkerRegistration] = useState<ServiceWorkerRegistration>();
  const [isOffline, setOffline] = useState(false);
  const [isBridge, setBridge] = useState(true);
  const { t } = useTranslation('common');

  const { state } = useContext(AppContext);
  const { get } = useApi()

  useEffect(()=>{
    if (process.env.NODE_ENV==='production') {
      serviceWorker.register({
        onSuccess: ()=>setServiceWorkerInitialized(true),
        onUpdate: (reg)=>{
          setServiceWorkerRegistration(reg);
          setServiceWorkerUpdated(true);
        }
      })
    }
    loadBridge()
  }, []);

  const loadBridge = () => {
    get(
      {url: '/bridge/'}
    ).then(data=>setBridge(data!==null)
    ).catch(()=>setBridge(false))
  }

  const tabBarSlot = isPlatform('mobile')?'bottom':'top'
  const tabBarLayout = isPlatform('mobile')?'icon-top':'icon-start'
  return (
    <IonApp>
      <HueConfig isOpen={!isBridge} onFinish={loadBridge} onAbbort={()=>{}}/>
      <InitialConfig isOpen={isPlatform("capacitor")&&!state?.server} />
      <OfflineScreen isOpen={isOffline}/>
      <IonToast
        isOpen={serviceWorkerInitialized}
        onDidDismiss={() => setServiceWorkerInitialized(false)}
        message={t('serviceWorker.initialized')}
        position='top'
        duration={5000}
      />
      <IonToast
        isOpen={serviceWorkerUpdated}
        message={t('serviceWorker.updated')}
        position='top'
        buttons={[
          {
            text: t('actions.update'),
            handler: () => {
              const registrationWaiting = serviceWorkerRegistration?.waiting;
              if (registrationWaiting) {
                registrationWaiting.postMessage({ type: 'SKIP_WAITING' });
                registrationWaiting.addEventListener('statechange', (e: any) => {
                  if (e.target.state === 'activated') {
                    window.location.reload();
                  }
                });
              }
            }
          }
        ]}
      />
      <IonReactRouter >
        <IonTabs>
          <IonRouterOutlet  >
            <Route exact path="/" render={() => <Redirect to="/start" />} />
            <Route exact path="/:tab(start)" component={TabStart} />
            <Route exact path='/:tab(lights)' component={PageLights} />
            <Route exact path='/:tab(lights)/:id' component={PageLightDetail} />
            <Route exact path="/:tab(groups)" component={PageGroups} />
            <Route exact path='/:tab(groups)/:id' component={PageGroupDetail} />
            <Route exact path="/:tab(curves)" component={PageCurves} />
            <Route exact path="/:tab(curves)/:id" component={PageCurveDetail} />
            <Route exact path="/:tab(settings)" component={TabSettings} />
          </IonRouterOutlet>
          <IonTabBar slot={tabBarSlot} >
            <IonTabButton tab="start" href="/start" layout={tabBarLayout}>
              <IonIcon icon={home} />
              <IonLabel>{t('tabs.home')}</IonLabel>
            </IonTabButton>
            <IonTabButton tab="lights" href="/lights" layout={tabBarLayout}>
              <IonIcon icon={bulb} />
              <IonLabel>{t('tabs.lights')}</IonLabel>
            </IonTabButton>
            <IonTabButton tab="groups" href="/groups" layout={tabBarLayout}>
              <IonIcon icon={grid} />
              <IonLabel>{t('tabs.groups')}</IonLabel>
            </IonTabButton>
            <IonTabButton tab="curves" href="/curves" layout={tabBarLayout}>
              <IonIcon src={appIcon} />
              <IonLabel>{t('tabs.curves')}</IonLabel>
            </IonTabButton>
            <IonTabButton tab="settings" href="/settings" layout={tabBarLayout}>
              <IonIcon icon={cog} />
              <IonLabel>{t('tabs.settings')}</IonLabel>
            </IonTabButton>
          </IonTabBar>
        </IonTabs>
      </IonReactRouter>
    </IonApp>
)};

export default App;


interface IOfflineScreenProps {
  isOpen: boolean
}
const OfflineScreen: React.FC<IOfflineScreenProps> = ({isOpen}) => (
  <IonModal isOpen={false}>
    <div className='lp-offline' >
      <div className='lp-offline-inner'>
        <img src={icon}/>
        <IonLabel>You are Offline</IonLabel>
      </div>
    </div>
  </IonModal>
)