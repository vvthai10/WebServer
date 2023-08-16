from api.index import createApp, conn ,cur
app = createApp()

if __name__ =='__main__':
    try:
        app.run(debug=True)
    except Exception as err:
        print(err)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
