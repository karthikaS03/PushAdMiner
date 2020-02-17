
-- Count of notifications per seed keyword
select seed_keyword , min(cnt), max(cnt), round(avg(cnt)) from (
select seed_keyword,sw_url,date(timestamp), count(notification_title) as cnt
	from notification_details n join
	seed_urls s on n.sw_url_id = s.seed_url_id
	group by seed_keyword,sw_url, date(timestamp)
	order by 1 ) as s
	group by s.seed_keyword


-- Count of notifications per service worker
select sw_url , min(cnt), max(cnt) from (
select sw_url, date(timestamp) , count(notification_title) as cnt
	from notification_details 
	group by sw_url, date(timestamp) order by 1) as s
	group by s.sw_url having min(cnt)!=max(cnt) order by sw_url
	

-- Count of distinct application server key per seed keyword
select seed_keyword, count(distinct l.app_server_key), string_agg(distinct l.app_server_key,',') from seed_urls s
join (
select d1.log_id, substring(d1.info,28) as app_server_key,  url_id from detailed_logs d1 join 
(select log_id+1 as log_id, info from detailed_logs where  info LIKE 'pushsubscription' ) AS foo
on d1.log_id = foo.log_id
) as l
on s.seed_url_id = l.url_id
group by seed_keyword

-- Count of  seed keyword per application server key 
select l.app_server_key, count(seed_keyword), count(distinct seed_url_id), string_agg(distinct seed_url,',') from seed_urls s
join (
select d1.log_id, substring(d1.info,28) as app_server_key,  url_id from detailed_logs d1 join 
(select log_id+1 as log_id, info from detailed_logs where  info LIKE 'pushsubscription' ) AS foo
on d1.log_id = foo.log_id
) as l
on s.seed_url_id = l.url_id
group by l.app_server_key
order by 3 desc

--Notification count per service worker

select sw_url , min(cnt), max(cnt), avg(cnt)::int from (
select sw_url, date(timestamp) , count(notification_title) as cnt
	from notification_details 
	group by sw_url, date(timestamp) order by 1) as s
	group by s.sw_url 
	--having min(cnt)!=max(cnt) 
	order by sw_url


--First Notification from each service worker
select * from
(
select distinct  d.target_url,d.timestamp,d.url_id, dd.timestamp
 ,dd.timestamp-d.timestamp
 ,EXTRACT(EPOCH FROM (dd.timestamp-d.timestamp)),
	date_part('minute',(dd.timestamp-d.timestamp)) as minutes
 ,rank() OVER (
          PARTITION BY d.url_id, d.target_url
          ORDER BY  d.iteration,d.timestamp, EXTRACT(EPOCH FROM (dd.timestamp-d.timestamp))
      ) as cnt
	  from desktop_detailed_logs d
join 
	(select url_id, iteration, trim(split_part(info,': ',2)) as url,timestamp from desktop_detailed_logs 
	 where info LIKE '%Notification from%' 
	 --and iteration=0
	) dd
	--notification_details n
--on n.sw_url= d.target_url and url_id=sw_url_id  and d.timestamp< n.timestamp
on d.url_id=dd.url_id and d.iteration=dd.iteration and trim(d.target_url) = dd.url and 
	EXTRACT(EPOCH FROM (dd.timestamp-d.timestamp))>0
and info LIKE '%Service Worker Registered' 
	--and d.iteration=0
order by d.url_id,d.timestamp,dd.timestamp
) first
where cnt=1
order by 6


---
--Total number of visited urls grouped by ad network
---

select seed_keyword,count(distinct s.seed_url) from seed_urls s
join 
(select distinct target_url from desktop_detailed_logs_latest 
 union
 select distinct target_url from desktop_detailed_logs_top 
 union
 select distinct target_url from desktop_detailed_logs_adblock
 union
 select distinct target_url from desktop_detailed_logs_adguard 
 union
 select distinct target_url from mobile_detailed_logs ) d 
on s.seed_url= d.target_url
where has_permission_request=true
group by seed_keyword


---
-- Total number of additinal urls visited by clicking notification
---


select  distinct landing_url --split_part(landing_url,'/',3)
from 
(select distinct landing_url,url from desktop_detailed_logs_latest 
 where info LIKE '%Notification shown%'
 union
 select distinct landing_url,url from desktop_detailed_logs_top 
  where info LIKE '%Notification shown%'
 union
 select distinct landing_url,url from desktop_detailed_logs_adblock
  where info LIKE '%Notification shown%'
 union
 select distinct landing_url,url from desktop_detailed_logs_adguard 
  where info LIKE '%Notification shown%'
 union
 select distinct landing_url,url from mobile_detailed_logs 
 where info LIKE '%Notification shown%') d
where landing_url<>'' and landing_url not in 
(select distinct seed_url from seed_urls where has_permission_request=true)




---
-- Total number of  urls that registered service workers
---


select distinct target_url --split_part(target_url,'/',3)
from 
(select distinct target_url from desktop_detailed_logs_latest 
 where info LIKE '%Service Worker Registered'
 union
 select distinct target_url  from desktop_detailed_logs_top 
 where info LIKE '%Service Worker Registered'
 union
 select distinct target_url  from desktop_detailed_logs_adblock
  where info LIKE '%Service Worker Registered'
 union
 select distinct target_url  from desktop_detailed_logs_adguard 
 where info LIKE '%Service Worker Registered'
 union
select distinct replace(split_part(info,':: ',2),'"','') as target_url from mobile_detailed_logs 
 where info LIKE '%Service Worker Registered%') d



---
-- Total number of  sw urls that sent notifications
---



select distinct sw_url --split_part(target_url,'/',3)
from 
(select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_latest 
 where info LIKE '%Notification shown%'
 union
 select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_top 
where info LIKE '%Notification shown%'
 union
 select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_adblock
  where info LIKE '%Notification shown%'
 union
 select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_adguard 
 where info LIKE '%Notification shown%'
 union
 select distinct sw_url from notification_details_mobile) d


---
-- Total number of  seed domains that sent notifications
---

select distinct split_part(sw_url,'/',3)
from 
(select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_latest 
 where info LIKE '%Notification shown%'
 union
 select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_top 
where info LIKE '%Notification shown%'
 union
 select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_adblock
  where info LIKE '%Notification shown%'
 union
 select distinct split_part(info,'&&',4) as sw_url from desktop_detailed_logs_adguard 
 where info LIKE '%Notification shown%'
 union
 select distinct sw_url from notification_details_mobile) d
 join 
 seed_urls s on split_part(seed_url,'/',3) = split_part(sw_url,'/',3)


---
-- Total number of  notifications
---


select distinct info,timestamp
from 
(select distinct info,timestamp  from desktop_detailed_logs_latest 
 where info LIKE '%Notification shown%'
 union
 select distinct info,timestamp  from desktop_detailed_logs_top 
where info LIKE '%Notification shown%'
 union
 select distinct info,timestamp  from desktop_detailed_logs_adblock
  where info LIKE '%Notification shown%'
 union
 select distinct info,timestamp  from desktop_detailed_logs_adguard 
 where info LIKE '%Notification shown%'
 union
 select distinct info,timestamp  from mobile_detailed_logs
 where info LIKE '%Notification shown%'
 union 
 select distinct info,timestamp  from desktop_detailed_logs
 where info LIKE '%Notification shown%') d
 