#! /usr/bin/env python3

import psycopg2

DB_NAME = "news"

# 1.1. Query to create a view for top articles
top_articles_create = "CREATE VIEW top_article_view AS " \
                      "SELECT " \
                      "title, " \
                      "author, " \
                      "count(*) AS total_views " \
                      "FROM articles, log " \
                      "WHERE " \
                      "log.path = concat('/article/', articles.slug) " \
                      "GROUP BY a" \
                      "rticles.title, articles.author " \
                      "ORDER BY total_views DESC;"

# 1.2. Query to get top three articles from the top articles view
top_articles_query = "SELECT title, total_views FROM top_article_view LIMIT 3"

# 2.1 Query to get top authors
top_authors_query = "SELECT " \
                    "authors.name                      AS \"name\", " \
                    "sum(top_article_view.total_views) AS author_views " \
                    "FROM top_article_view, authors " \
                    "WHERE authors.id = top_article_view.author " \
                    "GROUP BY \"name\" " \
                    "ORDER BY author_views DESC;"

# 3.1 Create an error view from logs
error_log_create = "CREATE VIEW error_log_view AS " \
                   "SELECT " \
                   "date(TIME), " \
                   "round(100.0 * sum( " \
                   "    CASE LOG.status " \
                   "WHEN '200 OK' " \
                   "THEN 0 " \
                   "ELSE 1 END) / count(LOG.status), 2) AS \"Percent Error\" "\
                   "FROM log " \
                   "GROUP BY date(TIME) " \
                   "ORDER BY \"Percent Error\" DESC;"

# 3.2 See days where there was more than 1% error in requests
error_log_query = "SELECT * FROM error_log_view WHERE \"Percent Error\" > 1;"


# Function to check if the views already exist or not
def view_exist():
    database = psycopg2.connect(database=DB_NAME)
    retVal = 1
    try:
        cursor = database.cursor()
        cursor.execute("SELECT EXISTS(SELECT * FROM top_article_view)")
        cursor.execute("SELECT EXISTS(SELECT * FROM error_log_view)")
    except:
        retVal = 0
    finally:
        database.close()
    return retVal


def create_views():
    db = psycopg2.connect(database=DB_NAME)
    cursor = db.cursor()
    cursor.execute(top_articles_create)
    cursor.execute(error_log_create)
    db.commit()
    db.close()
    pass


# Function to print the query results
def print_results(queryResult, ending):
    for res in queryResult:
        print('\t' + str(res[0]) + ' ---> ' + str(res[1]) + ' ' + ending)


if __name__ == '__main__':
    if (view_exist() == 0):
        print("Creating new views")
        create_views()
    db = psycopg2.connect(database=DB_NAME)
    cursor = db.cursor()

    cursor.execute(top_articles_query)
    print("\n1. The 3 most popular articles of all time are: ")
    print_results(cursor.fetchall(), 'views')

    cursor.execute(top_authors_query)
    print("\n2. The most popular article authors of all time are: ")
    print_results(cursor.fetchall(), 'views')

    cursor.execute(error_log_query)
    print("\n3. Days with more than 1% of requests leading to error: ")
    print_results(cursor.fetchall(), '%')
    db.close()
