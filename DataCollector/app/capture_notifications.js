
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

  var home_dir= '/home/pptruser/'
  
  await puppeteer.launch({ headless:false,  executablePath:home_dir+'chromium/chrome',
                           userDataDir:home_dir+'chrome_user/',
                           args: [
                                  '--enable-features=NetworkService',
                                  '--no-sandbox',
                                  '--disable-setuid-sandbox',
                                  '--window-size=${ width },${ height }',
                                  //'--start-maximized',
                                  '--ignore-certificate-errors','--disable-gpu', 
                                  //'--disable-extensions-except='+home_dir+'app/adGuard',
                                  //'--load_extension = '+home_dir+'app/adGuard'                                                           
                                ]
                         }).then(async browser => 
    {
        
      var sw_log_dir = home_dir+'logs/'
      var stream = fs.createWriteStream(sw_log_dir+id+"_sw.log");
       
      try{
          var the_interval = wait_time *1000 //in milliseconds

          var page_dir = home_dir+'screenshots/'+id+'/pages/'          
          var resources_path = home_dir+'resources/'+id+'/'

          if (!fs.existsSync(resources_path)){
            fs.mkdirSync(resources_path);
          }

          /*Get screenshot whenever new tab opens and close page after 5 minutes */
          browser.on('targetcreated', async function(target){    
        
              if(target._targetInfo.type=='page'){
                var p = await target.page()                
                p.once('load',  async function(){
                  console.log('page loaded')
                  try{
                    try{
                    await p.waitForNavigation('networkidle2', timeout=900000)}
                    catch(e)
                    {
                      console.log('timeout!!')
                    }
                    var img_dir = home_dir+'screenshots/'+id
                    var content_dir =  home_dir+'resources/'+id
                    var domain = p.url().split('/')[2]
                    var time = new Date().getTime()
                    await p.screenshot({ path: img_dir+'_'+i_count+'_'+ domain+'_'+time+'_page.png', type: 'png' });
                    const html = await p.content()
                    fs.writeFile( content_dir+'_'+i_count+'_'+ domain+'_'+time+'.html', html, (err) => {
                      // throws an error, you could also catch it here
                      if (err) console.log(err);
                      // success case, the file was saved
                      console.log('Content saved!');
                  });
                  
                    console.log('screen captured')
                  }catch(e){
                    console.log(e)
                  }
                  
                })
                
                await setTimeout(async function() {
                    await p.close()
                }, 180000)		
            }
          })
          
          const page = await browser.newPage();
          await page.setViewport({ width, height })
          const context = browser.defaultBrowserContext();
          /** Log site details */
          stream.write('[Visiting Page started @ '+new Date(Date.now()).toLocaleString()+' ]');
          stream.write('\n')
          stream.write('\tID :: ' +id);
          stream.write('\n')
          stream.write('\tURL :: ' +url) 
          stream.write('\n')
          var service_workers_hooks = {}

          /*Initial Visit :: Attach event handler to log all requests sent by service worker*/
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
                  var dir = home_dir+'screenshots/'+id
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

          
          var wait_interval = 5000
          count=0  
          
          var trigger = await setInterval(async function() 
          {
            if (count >= the_interval )
            {      
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
          
            /* Capture Screenshot of the whole desktop including the notification every 15secs */
            var screenshot = require('screenshot-desktop');
            var dir = home_dir+'screenshots/'+id
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
           

            /* Resumed Container :: Browse thhrough all service workers and create hooks on the methods*/
            await browser.serviceWorkers().then(async function(service_workers) {	
              	
              if (service_workers.length>0)              
              {
                service_workers.forEach( async sw => 
                {   
                  if (sw._status=='active')
                  {
                    if (!(sw.url() in service_workers_hooks))
                        service_workers_hooks[sw.url()] =1
                    else
                      return              
                    stream.write('\t\tSW Status :: Active') 

                    /* Save the response content . Need to be modified for saving image content*/
                    sw.on('response',  async res => {                        
                      try{
                        var file_name = res.url().split('/').pop()
                        var text = await res.text()
                        fs.writeFile(resources_path+file_name, text, 'utf8', (err) => {              
                          stream.write('\t\tResponse file saved');
                        });
                      }
                      catch(error){
                        console.log('response text no body found')
                      }
                         
                    })                
                    //
                    /* Capture all Requests made byy  Service Worker Scripts */
                    sw.on('request',  async req => {
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
            /* Don't close the page. Causes problem when resuming */
            //await page.close()
          })
        }, wait_interval);

        try{
          console.log('visiting page')
          await page.goto(url);
        }
        catch(err){
          console.log(id+" :: page load timeout")
        }
        
        console.log('page visited')
               

     }
     catch(error)
     {
        stream.write('ERROR::'+error)        
        console.log(error)
        return  
     }
        
  });
  return true
};

//const timeoutPromise = (timeout) => new Promise((resolve) => setTimeout(resolve, timeout));

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
