require 'date'



def get_where_clause(type, start_date, end_date)
  # Default Type Param
  if type.nil?
    type = 'monthly'
  end

  # Default Start Date
  if start_date.nil?
    start_date = Date.parse("01/01/2023")
  else
    start_date = Date.parse(start_date)
  end

  # Default End Date
  if end_date.nil?
    end_date = Date.today
  end

  # Where Clause Builder
  # start_date will take priority over end_date
  case type
  when 'daily'
    where_clause = "WHERE (date = #{start_date.strftime("%Y-%m-%d")}"
  when 'weekly'
    date_today = start_date.strftime("%Y-%m-%d")
    seven_days_ago = (Time.now - 7*24*60*60).strftime("%Y-%m-%d")
    where_clause = "WHERE (date BETWEEN #{seven_days_ago} AND #{date_today})"
  when 'monthly'
    date_today = start_date.strftime("%Y-%m-%d")
    first_day_of_month = start_date.beginning_of_month
    where_clause = "WHERE (date BETWEEN #{first_day_of_month} AND #{date_today})"
  when 'yearly'
    date_today = start_date.strftime("%Y-%m-%d")
    first_day_of_year = date_today.beginning_of_year
    where_clause = "WHERE (date BETWEEN #{first_day_of_year} AND #{date_today})"
  when 'lifetime'
    where_clause = ""
  else
    where_clause = "WHERE (date BETWEEN #{start_date.strftime("%Y-%m-%d")} AND #{end_date.strftime("%Y-%m-%d")})"
  end
  where_clause
end


type = nil
start_date = nil
end_date = nil
where_clause = get_where_clause(type, start_date, end_date)
command = "SELECT uuid, SUM(amount) as total_exp FROM expHistory#{where_clause} GROUP BY uuid ORDER BY total_exp DESC"
puts command