
'use strict';

const puppeteer = require('puppeteer');
const devices = require('puppeteer/DeviceDescriptors');
const nexus = devices['Nexus 5'];
var fs = require('fs');
var fs_extra = require('fs-extra')


process.on('unhandledRejection', error => {
  // Prints "unhandledRejection woops!"
  console.log(site_id+' :: '+url)
	console.log('unhandledRejection', error);
});

async function load_page(url,id,i_count,wait_time){
  var count = 0
  
  // Viewport && Window size
  const width = 650
  const height = 1020
  
  await puppeteer.launch({ headless:false,  executablePath:'/home/pptruser/chromium/chrome',
                           userDataDir:'/home/pptruser/chrome_user/',
                           args: [
                                '--enable-features=NetworkService',
                                '--no-sandbox',
                                '--disable-setuid-sandbox',
                                '--window-size=${ width },${ height }',
                                //'--start-maximized',
                                '--ignore-certificate-errors','--disable-gpu', '--disable-software-rasterizer', '--disable-infobars' ]
                         }).then(async browser => 
    {
        
        var sw_log_dir = '/home/pptruser/logs/'
        var stream = fs.createWriteStream(sw_log_dir+id+"_sw.log");
       
        try{
          var the_interval = wait_time *1000 //in milliseconds
          var page_dir = '/home/pptruser/screenshots/'+id+'/pages/'
          
          var resources_path = '/home/pptruser/resources/'+id+'/'

          if (!fs.existsSync(resources_path)){
            fs.mkdirSync(resources_path);
          }

          /*Get screenshot whenever new tab opens*/
          browser.on('targetcreated', async function(target){    
        
              if(target._targetInfo.type=='page'){
                var p = await target.page()
                await setTimeout(async function() {                  
                   var screenshot = require('screenshot-desktop');
                    var dir = '/home/pptruser/screenshots/'+id
                    if (!fs.existsSync(dir)){
                      fs.mkdirSync(dir);
                    }
                    dir = dir +'/pages/'
                    if (!fs.existsSync(dir)){
                          fs.mkdirSync(dir);
                    }                    
                    //await p.screenshot({ path: dir+id+'_'+i_count+'_'+target._targetId+'_page.png', type: 'png' });

                    var file_name = dir+id+'_'+i_count+'_'+target._targetId+'.png';
                    await screenshot({screen:'screen',filename:file_name}).then(function(complete) {													
                        return ''
                    });                    
                    await p.close()
                }, 180000)		
            }
          })
          
          const page = await browser.newPage();
          await page.setViewport({ width, height })

          //await page.emulate(nexus)

          const context = browser.defaultBrowserContext();
          
          await setTimeout(async function() {                  
            var screenshot = require('screenshot-desktop');
             var dir = '/home/pptruser/screenshots/'+id
             if (!fs.existsSync(dir)){
               fs.mkdirSync(dir);
             }
             dir = dir +'/pages/'
             if (!fs.existsSync(dir)){
                   fs.mkdirSync(dir);
             }
             var file_name = dir+id+'_'+i_count+'_initial'+'.png';
             await screenshot({screen:'screen',filename:file_name}).then(function(complete) {													
                 return ''
             });
         }, 15000)		
          
          /** Log site details */
          stream.write('[Visiting Page started @ '+new Date(Date.now()).toLocaleString()+' ]');
          stream.write('\n')
          stream.write('\tID :: ' +id);
          stream.write('\n')
          stream.write('\tURL :: ' +url) 
          stream.write('\n')
          var service_workers_hooks = {}
          /*Attach event handler to log all requests sent by service worker*/
          browser.on('serviceworkercreated', async sw => {
            stream.write('\t||')
            stream.write('\n')
            stream.write('\t\t[Service Worker Registered @ '+ new Date(Date.now()).toLocaleString() +' ]')
            stream.write('\n')
            stream.write('\t\tSW URL :: '+sw.url())         
            stream.write('\n') 
            stream.write('\t||')   
            stream.write('\n')
            if (sw._status=='new'){
              stream.write('\t\tSW Status :: New')   
              stream.write('\n')
              if (!(sw.url() in service_workers_hooks))
                  service_workers_hooks[sw.url()] =1
              sw.on('response',  async res => {
                //stream.write(res.url())  
                try{
                var file_name = res.url().split('/').pop()
                var text = await res.text()
                fs.writeFile(resources_path+file_name, text, 'utf8', (err) => {              
                  stream.write('\t\tResponse file saved');
                });}
                catch(err){console.log(err)}
                //await console.log(text)    
              })  
              

              sw.on('request',  async req => {

               setTimeout(async function() {                  
                  var screenshot = require('screenshot-desktop');
                  var ids = req._requestId.split('.')
                  var dir = '/home/pptruser/screenshots/'+id
                  if (!fs.existsSync(dir)){
                    fs.mkdirSync(dir);
                  }
                  dir = dir +'/'+ids[0]+'/'
                  if (!fs.existsSync(dir)){
                        fs.mkdirSync(dir);
                  }
                  await screenshot({screen:'screen',filename:dir+ids[1]+'_push.png'}).then(function(complete) {													
                      return ''
                  });
                }, 15000)
                stream.write('\t***')              
                stream.write('\n')
                stream.write('\t\t[Service Worker Request called @ '+new Date(Date.now()).toLocaleString() + ' ]')   
                stream.write('\n')        
                stream.write('\t\tRequest Id :: ' + req._requestId)    
                stream.write('\n')
                stream.write('\t\tRequest Origin :: ' + req._headers.referer)       
                stream.write('\n')               
                stream.write('\t\tRequest URL :: ' + req.url())
                stream.write('\n')
                  if (req._postData!=undefined){
                    stream.write('\t\tPost Data :: '+ req._postData)
                    stream.write('\n')
                  }
                  if (req._redirectChain.length>0){
                    stream.write('\t\t***Redirections***')
                    stream.write('\n')
                    //console.log(req._redirectChain)
                    var redirect_chain = req._redirectChain
                    if (redirect_chain.length>0){
                      redirect_chain.forEach(redirect => {                     
                        stream.write('\t\tRedirect Origin :: ' + redirect._headers.referer)  
                        stream.write('\n')                    
                        stream.write('\t\tRedirect URL :: ' + redirect.url())
                        stream.write('\n')
                      });
                    }
                    stream.write('\t\t***Redirections End***')
                    stream.write('\n')
                  }
                    
                  stream.write('\t***')
                  		
              }) 
            }       
          })

          try{
            console.log('visiting page')
            await page.goto(url);
          }
          catch(err){
            console.log(id+" :: page load timeout")
          }
          //await page.waitFor(4000); 
          console.log('page visited')
          console.log(the_interval)
          var wait_interval = 5000
          count=0          
          
          var trigger = await setInterval(async function() {
            if (count >= the_interval ){      
              console.log(new Date(Date.now()).toLocaleString())
              stream.write('[Visiting Page ended @ '+new Date(Date.now()).toLocaleString()+' ]')
              stream.write('\n')
              stream.write('\n')
              //await browser.close();
              console.log('visit ended')    
              clearInterval(trigger);      
              await process_ended(id)
              return   
            }
            count = count+wait_interval     
            //console.log(count)

            var screenshot = require('screenshot-desktop');
            var dir = '/home/pptruser/screenshots/'+id
            if (!fs.existsSync(dir)){
              fs.mkdirSync(dir);
            }
            dir = dir +'/pages/'
            if (!fs.existsSync(dir)){
                  fs.mkdirSync(dir);
            }
            var file_name = dir+id+'_'+i_count+'_'+count+'_status.png';
            await screenshot({screen:'screen',filename:file_name}).then(function(complete) {													
                return ''
            });


            await browser.serviceWorkers().then(async function(service_workers) {	
              //console.log(service_workers)	
              if (service_workers.length>0){
              service_workers.forEach( async sw => {   
                //console.log(sw)                 
                  if (sw._status=='active'){
                    if (!(sw.url() in service_workers_hooks))
                        service_workers_hooks[sw.url()] =1
                    else
                      return
                    //console.log(sw)
                    stream.write('\t\tSW Status :: Active')   
                    //stream.write('\n')
                    sw.on('response',  async res => {
                      //stream.write(res.url())  
                      try{
                      var file_name = res.url().split('/').pop()
                      var text = await res.text()
                      fs.writeFile(resources_path+file_name, text, 'utf8', (err) => {              
                        stream.write('\t\tResponse file saved');
                      });}
                      catch(error){
                        console.log('response text no body found')
                      }
                      //await console.log(text)    
                    })                     
                    sw.on('request',  async req => {
                     /*
                    setTimeout(async function() {                  
                        var screenshot = require('screenshot-desktop');
                        var ids = req._requestId.split('.')
                        var dir = '/home/pptruser/screenshots/'+id
                        if (!fs.existsSync(dir)){
                          fs.mkdirSync(dir);
                        }
                        dir = dir +'/'+ids[0]+'/'
                        if (!fs.existsSync(dir)){
                              fs.mkdirSync(dir);
                        }
                        await screenshot({screen:'screen',filename:dir+ids[1]+'_push.png'}).then(function(complete) {													
                            return ''
                        });
                      }, 100)*/
                      stream.write('\t***')              
                      stream.write('\n')
                      stream.write('\t\t[Service Worker Request called @ '+new Date(Date.now()).toLocaleString() + ' ]')   
                      stream.write('\n')        
                      stream.write('\t\tRequest Id :: ' + req._requestId)    
                      stream.write('\n')
                      stream.write('\t\tRequest Origin :: ' + req._headers.referer)       
                      stream.write('\n')               
                      stream.write('\t\tRequest URL :: ' + req.url())
                      stream.write('\n')
                        if (req._postData!=undefined){
                          stream.write('\t\tPost Data :: '+ req._postData)
                          stream.write('\n')
                        }
                        if (req._redirectChain.length>0){
                          stream.write('\t\t***Redirections***')
                          stream.write('\n')
                          //console.log(req._redirectChain)
                          var redirect_chain = req._redirectChain
                          if (redirect_chain!=undefined){
                            redirect_chain.array.forEach(redirect => {                     
                              stream.write('\t\tRedirect Origin :: ' + redirect._headers.referer)  
                              stream.write('\n')                    
                              stream.write('\t\tRedirect URL :: ' + redirect.url())
                              stream.write('\n')
                            });
                          }
                          stream.write('\t\t***Redirections End***')
                          stream.write('\n')
                        }
                          
                        stream.write('\t***')
                            
                    }) 
                  }       
              
              })
            }
            //await page.close()
          })
        }, wait_interval);
  
        }
        catch(error){
          stream.write('ERROR::'+error)        
          console.log(error)
          /*
          try{
            await browser.close();
          }
          catch(error){}
          */
          return  
          
          /*
          await fs_extra.move('/home/pptruser/chromium/chrome_debug.log', '/home/pptruser/logs/notification_'+(id)+'.log', function (err) {
              if (err) 
                return console.error(err)
              stream.write("LOG::saved after error")
             })   
          */
        }
        
  });
  return true
};
const timeoutPromise = (timeout) => new Promise((resolve) => setTimeout(resolve, timeout));

async function process_ended(id){
  console.log('crawl process ended :: '+id) 	
}

async function crawl_url(url, id, i_count,timeout){
      try{
        console.log('crawling started :: ' +id)
        await load_page(url,id, i_count,timeout)   
        //await timeoutPromise(timeout)
        
      }
      catch(error){
        console.log(error)        
      } 
}

if (process.argv[2]) {
  var url = process.argv[2];
  var site_id =process.argv[3];  
  var i_count = process.argv[4];
  var timeout = process.argv[5];
  
  
  crawl_url(url,site_id,i_count,timeout)
  
}
