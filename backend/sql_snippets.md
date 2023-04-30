# Collection of SQL Snippets

Here are find some SQL queries to inspect the current OA postgres DB.

# Baics Stats

```sql
-- tables row counts
(select 'user' as "table", count(*) from "user") union
(select 'task', count(*) from task) union
(select 'message_tree_state', count(*) from message_tree_state) union
(select 'message_reaction', count(*) from message_reaction) union
(select 'text_labels', count(*) from text_labels) union
(select 'message', count(*) from message) union
(select 'journal', count(*) from journal);
```

# Messages

```sql
-- only human by role
select role, count(*)
from message
where not deleted and review_result and not synthetic
group by role;
```

```sql
-- language distribution of messages (incl. synthetic)
select lang, count(*), synthetic from message where not deleted and review_result
group by lang, synthetic;
```

```sql
-- only human generated messages by lang
select lang, count(*)
from message
where not deleted and review_result and not synthetic
group by lang;
```

## Message Trees

```sql
-- total count of message trees
select count(*) from message_tree_state;
```

```sql
-- message tree counts by state
select state, count(*) from message_tree_state group by state;
```

```sql
-- count of waiting initial prompts by language
select m.lang, count(*)
from message_tree_state mts
  join message m on mts.message_tree_id = m.id
where mts.state = 'prompt_lottery_waiting'
group by m.lang;
```

```sql
-- message trees by lang in ready_for_export or growing state
select m.lang, mts.state, count(*)
from message_tree_state mts
  join message m on mts.message_tree_id = m.id
where mts.state in ('ready_for_export', 'growing')
group by mts.state, m.lang
order by lang, state;
```

```sql
-- select message tree counts
select mts.message_tree_id, count(m.id), max(m.depth), count(m.id) filter (where m.role='prompter') as prompter, count(m.id) filter (where m.role='assistant') as assistant
from message_tree_state mts
  join message m on mts.message_tree_id = m.message_tree_id
where mts.state='growing'
  and not m.deleted
  and m.review_result=true
  and m.lang='en'
  and mts.active
group by mts.message_tree_id
order by count(m.id) desc;
```

```sql
-- show top 100 largest trees
select mts.message_tree_id, mts.goal_tree_size, mts.state, count(m.id) as message_count
from message_tree_state mts
  join message m on mts.message_tree_id = m.message_tree_id
where not m.deleted and m.review_result=true
group by mts.message_tree_id, mts.state
order by count(m.id) desc
limit 100;
```

```sql
-- active trees, current & goal_size
select mts.message_tree_id, mts.state, mts.goal_tree_size, count(m.id) AS tree_size, max(m.depth) AS max_depth
from message_tree_state mts
    join message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active
    and not m.deleted
    and m.review_result
group by mts.message_tree_id, mts.goal_tree_size;
```

## Users

```sql
-- count users that accepted tos
select count(*) from "user" where tos_acceptance_date is not null;
```

```sql
-- last 25 active users
select u.id, u.username, u.auth_method, u.display_name, u.last_activity_date, age(current_timestamp, last_activity_date) from "user" u WHERE u.last_activity_date is not null order by u.last_activity_date desc limit 25;

select id, display_name, username, auth_method, last_activity_date from "user" where age(last_activity_date) < interval '1 minutes' order by last_activity_date desc limit 25;
```

```sql
-- count active users in last 5 mins
select count(*) from "user" u where age(current_timestamp, last_activity_date) < interval '5 mins';

```

```sql
-- total count of non-deleted messages (human + synth)
select count(*) from message where deleted=false and review_result=true;
```

```sql
-- count max, mean message counts per tree for a given language
with t(message_tree_id, tree_size, state) as (select mts.message_tree_id, count(m.id), mts.state
from message_tree_state mts
  join message m on mts.message_tree_id = m.message_tree_id
where
  not m.deleted
  and m.review_result=true
  and m.lang = 'en'
group by mts.message_tree_id)
select state, count(t.*) as trees, sum(t.tree_size) as total_msgs, max(t.tree_size), avg(t.tree_size) from t group by t.state;
```

## Tasks

```sql
-- average time between task creation and completion
(select t.payload#>>'{payload, type}' as type, count(*), avg(r.created_date-t.created_date)
from task t
  join message_reaction r on t.id = task_id
where t.done and not t.skipped group by t.payload#>>'{payload, type}') union
(select t.payload#>>'{payload, type}' as type, count(*), avg(l.created_date-t.created_date)
from task t join
  text_labels l on t.id = l.task_id
where t.done and not t.skipped group by t.payload#>>'{payload, type}') union
(
select t.payload#>>'{payload, type}' as type, count(*), avg(m.created_date-t.created_date)
from task t join
  message m on t.id = m.task_id
where t.done and not t.skipped group by t.payload#>>'{payload, type}');
```

## Connections

```sql
-- from https://dba.stackexchange.com/questions/161760/number-of-active-connections-and-remaining-connections
select max_conn,used,res_for_super,max_conn-used-res_for_super res_for_normal
from
  (select count(*) used from pg_stat_activity) t1,
  (select setting::int res_for_super from pg_settings where name=$$superuser_reserved_connections$$) t2,
  (select setting::int max_conn from pg_settings where name=$$max_connections$$) t3;
```
