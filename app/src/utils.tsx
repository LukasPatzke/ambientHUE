import { Plugins } from '@capacitor/core';
import { isPlatform } from '@ionic/react';

const { Storage } = Plugins;

export const api = () => {
  const server = Storage.get({key:'apiServer'});
  const port = Storage.get({key:'apiPort'});
  const ssl = Storage.get({key:'apiSsl'});

  return Promise.all([server, port, ssl]).then(([server, port, ssl])=>{
    return new Promise<string>((resolve, reject)=>{
      if (isPlatform('desktop') || isPlatform('mobileweb') ) {
        resolve('/api')
      } else {
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
      }
    })
  })
}


export const range = (start: number, stop?: number, step?: number) => {
  if (typeof stop == 'undefined') {
    // one param defined
    stop = start;
    start = 0;
  }

  if (typeof step == 'undefined') {
    step = 1;
  }

  if ((step > 0 && start >= stop) || (step < 0 && start <= stop)) {
    return [];
  }

  var result: number[] = [];
  for (var i = start; step > 0 ? i < stop : i > stop; i += step) {
    result.push(i);
  }

  return result;
};