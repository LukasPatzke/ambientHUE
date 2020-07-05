import { Plugins } from '@capacitor/core';
import { isPlatform } from '@ionic/react';
import { resolve } from 'dns';

const { Storage } = Plugins;

interface IApiOptions {
  url: string
  data?: any
}

interface IGetOptions {
  url: string
}
interface IPostOptions extends IGetOptions {
  data: any
}
interface IDeleteOptions extends IGetOptions {}
interface IPutOptions extends IPostOptions {}

export const useApi = () => {
  const server = Storage.get({key:'apiServer'});
  const port = Storage.get({key:'apiPort'});
  const ssl = Storage.get({key:'apiSsl'});

  const api = (method: 'GET'|'POST'|'PUT'|'DELETE', options: IApiOptions) => {
    let baseUrl: Promise<string>;
    if (isPlatform('desktop') || isPlatform('mobileweb') ) {
      baseUrl = new Promise<string>((resolve)=>resolve('/api'))
    } else {
      baseUrl = Promise.all([server, port, ssl]).then(([server, port, ssl])=>{
        return new Promise<string>((resolve, reject)=>{
          if ((!server.value) || (server.value==='')) {
            reject('server not in storage')
          } else {
            var url='';
            if (ssl.value==='true') {url+='https://'} else {url+='http://'}
            url += server.value;
            if (port.value!=='null') {url+=`:${port.value}`}
            url += '/api'
            resolve(url)
          }
        })
      })
    }
    return baseUrl.then(baseUrl=>(
      fetch(baseUrl + options.url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        redirect: 'follow',
        body: JSON.stringify(options.data)
      })
    )).then(response=>response.json())
  }

  return {
    get: (options: IGetOptions) => api("GET", options),
    post: (options: IPostOptions) => api("POST", options),
    put: (options: IPutOptions) => api("PUT", options),
    delete: (options: IDeleteOptions) => api("DELETE", options),
  } 
}
