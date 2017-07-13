# soundcloud-enumerate

<img align="right" src="https://image.freepik.com/freie-ikonen/soundcloud-logo_318-65089.jpg"> 

> Instead, sources at SoundCloud tell TechCrunch that founders Alex Ljung and Eric Wahlforss confessed the layoffs only saved the company enough money to have runway “until Q4” — which begins in just 80 days. 

SoundCloud is officially going down, and with it over 150 million songs uploaded by the community...  
Well, maybe not. The SoundCloud API can be abused to enumerate users whose songs can then be downloaded by a tool like [scdl](https://github.com/flyingrub/scdl). I don't have enough storage or bandwidth to do so but you might.

### Approach
An [sqlite3](https://www.sqlite.org/) database (`soundcloud.db`) is used to store all users that have at least one public song. 

```sql
create table User (
	id integer primary key,
	username text not null,
	permalink_url text not null,
	track_count integer not null
);
```

These should be enough fields to download all songs, most tools only require `permalink_url`.

### Setup
Environment variables:
* `CLIENT_ID`: [Stack Overflow](https://stackoverflow.com/questions/40992480/getting-a-soundcloud-api-client-id)