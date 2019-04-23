const puppeteer = require('puppeteer');
var fs_extra = require('fs-extra')
var fs = require('fs');


process.on('unhandledRejection', error => {
	console.log('unhandledRejection', error);
});

load_page = function(url,id){
	// Viewport && Window size
	const width = 1360
	const height = 1020
	puppeteer.launch({headless:false,executablePath:'/home/pptruser/chromium/chrome',
			args: ['--enable-features=NetworkService',
				'--no-sandbox',
				'--disable-setuid-sandbox',
				'--window-size=${ width },${ height }'
			]
		}).then(async browser => {
			var sw_log_dir = '/home/pptruser/logs/'
			var stream = fs.createWriteStream(sw_log_dir+id+"_sw.log");
			try{
				const page = await browser.newPage();			
				await page.setViewport({ width, height })
				
				
			 	/** Log site details */
				stream.write('[Visiting Page started @ '+new Date(Date.now()).toLocaleString()+' ]');
				stream.write('\n')
				stream.write('\tID :: ' +id);
				stream.write('\n')
				stream.write('\tURL :: ' +url) 
				stream.write('\n')
				await page.goto(url,{waitUntil: 'networkidle0', timeout: 300000});
				stream.write('\n[Page Load Complete @ '+new Date(Date.now()).toLocaleString()+' ]')
				await page.waitFor(6000);			
				await browser.close();
				stream.write('[Visiting Page ended @ '+new Date(Date.now()).toLocaleString()+' ]');
				stream.end();				
				/*
				await fs_extra.move('/home/pptruser/chromium/chrome_debug.log', '/home/pptruser/logs/permission_'+(id)+'.log', function (err) {
						if (err) 
							console.log(err)
						else
							console.log("LOG::saved")
					 })*/
			}
			catch(error){
				stream.write('[Chromium Crashed @ '+new Date(Date.now()).toLocaleString()+' ]');
				stream.write('Error ::' + error)
				stream.end();
			}
		});
}

if (!process.argv[2]) {
    process.exit(1);
}

var url = process.argv[2];
var id =process.argv[3];
load_page(url,id)
