drop table if exists all_sprocket_ids;

drop table if exists all_mledb_ids;

create temp table all_sprocket_ids as
select
	u.id as "user",
	uaa.id as "auth_acct",
	m.id as "member",
	mpa.id as "member_platform_account",
	p.id as "player"
from
	sprocket.user u
inner join sprocket.user_authentication_account uaa on
	uaa."userId" = u.id
inner join sprocket.member m on
	m."userId" = u.id
inner join sprocket.member_platform_account mpa on
	m.id = mpa."memberId"
inner join sprocket.player p on
	p."memberId" = m.id
where
	uaa."accountId" = '1121581950734438411';

create temp table all_mledb_ids as 
select 
	mlep.id as "mle_player",
	mlepa.id as "mle_player_account"
from
	mledb.player mlep
inner join mledb.player_account mlepa on
	mlepa.player_id = mlep.id
where
	mlep.discord_id = '1121581950734438411';

delete
from
	mledb.psyonix_api_result par
where
	par.player_account_id in (
	select
		mle_player_account
	from
		all_mledb_ids);

delete
from
	mledb.player_account pa
where
	pa.id in (
	select
		mle_player_account
	from
		all_mledb_ids);

delete
from
	mledb.eligibility_data ed
where
	ed.player_id in (
	select
		mle_player
	from
		all_mledb_ids);

delete
from
	mledb.player p
where
	p.id in (
	select
		mle_player
	from
		all_mledb_ids);

delete
from
	sprocket.player_stat_line psl
where
	psl."playerId" in (
	select
		player
	from
		all_sprocket_ids);

delete
from
	sprocket.eligibility_data ed
where
	ed."playerId" in (
	select
		player
	from
		all_sprocket_ids);

delete
from
	sprocket.player p
where
	p.id in (
	select
		player
	from
		all_sprocket_ids);

delete
from
	sprocket.member_platform_account mpa
where
	mpa.id in (
	select
		member_platform_account
	from
		all_sprocket_ids);

delete
from
	sprocket.member_profile mp
where
	mp."memberId" in (
	select
		member
	from
		all_sprocket_ids);

delete
from
	sprocket.member m
where
	m.id in (
	select
		member
	from
		all_sprocket_ids);

delete
from
	sprocket.user_authentication_account uaa
where
	uaa.id in (
	select
		auth_acct
	from
		all_sprocket_ids);
