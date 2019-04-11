const puppeteer = require('puppeteer');
var fs_extra = require('fs-extra')

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
			const page = await browser.newPage();			
			await page.setViewport({ width, height })
			await page.goto(url,{waitUntil: 'networkidle0', timeout: 100000});
			await page.waitFor(6000);			
			await browser.close();
			await fs_extra.move('/home/pptruser/chromium/chrome_debug.log', '/home/pptruser/logs/permission_'+(id)+'.log', function (err) {
					if (err) 
						console.log("LOG::error saving")
					else
						console.log("LOG::saved")
				 })
		});
}

if (!process.argv[2]) {
    process.exit(1);
}

var url = process.argv[2];
var id =process.argv[3];
load_page(url,id)
