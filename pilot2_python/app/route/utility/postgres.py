import psycopg2

# 테스트용 환경변수 강제 설정 = 이후 환경변수에서 바로 접속하도록 설정할 것
host = "app-db"
port = 5432
dbname = "mp_db"
user = "admin"
password = "visumy00"


class postgres:
    def __init__(self):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password


    def conn(self):
        try:
            return psycopg2.connect(
                host = self.host,
                port = self.port,
                dbname = self.dbname,
                user = self.user,
                password = self.password
                )
        except:
            return print("[ERROR] Connection Error")

    def cur(self):
        try:
            return self.db().cursor()
        except:
            return print("[ERROR] Check cur")
    
    def CRUD(self, text):
        try:
            self.cur().execute(text)
            self.conn().commit()
        except:
            return print("[ERROR] Check query")


    # placeholder 사용
    def CRUD2(self, text, value):
        try:
            self.cur().execute(text, value)
            self.conn().commit()
        except:
            return print('[ERROR] Check query2')


    def SELECT(self, text):
        try:
            self.cur().execute(text)
            return self.cur().fetchall()
        except:
            return print("[ERROR] Check SELECT")


    # 프론트 액션에 필요한 쿼리 시작
    def login(self, username):
        try:
            text = f"SELECT account_id, password FROM public.user WHERE account_id = '{username}'"
            result = self.SELECT(text)
            return result
        except:
            return print("[ERROR] check Login")


    def current_data(self):
        try:
            currentData = {
                "id": int(1),
                "workspace_id": "", #string uuid 형태
                "workspace_name": "Jaehoon - Study",
                "workspace_desc": "For study to make backend by Python",
                "platform_name": "Python",
                "bind_code": "qwe"
            }
            return currentData
        except:
            return print("[ERROR] check current_data")


    def user_data(self, columns, table):
        try:
            text = f"SELECT {columns} FROM {table}"
            row = self.SELECT(text)
            result = {
              "mqtt_addr": emqx,
              "mqtt_username": "pilot",
              "mqtt_password": "pilot123",
              "username": row.username,
              "user_id": row.user_id,
              "workspace_id": row.workspace_id,
              "user_type": int(2)}
            return result
        except:
            return print("[ERROR] check user_data")


    def wayline_data(self):
        try:
            text = """SELECT oss_path->>'object_key' as object_key,
                      oss_path->>'wayline_id' as wayline_id,
                      oss_path->>'template_types' as template_types
                      FROM public.waypoint_plan
                      WHERE oss_path is not null;"""
            result = self.SELECT(text)
            return result
        except:
            return print("[ERROR] check wayline_data")


    def insert_wayline(self, wpml_info, oss_path):
        try:
            text = f"INSERT INTO public.waypoint_plan (wpml_info, oss_path) VALUES ({wpml_info}, {oss_path})"
            result = self.CRUD(text)
            return result
        except:
            return print("[ERROR] check insert_wayline")
    

    def update_wayline(self, wpml_info, oss_path, object_key):
        # object_key는 json이어야한다.
        try:
            text = f"""UPDATE public.waypoint_plan
                       SET wpml_info = {wpml_info}, oss_path = {oss_path}
                       WHERE oss_path @> "{object_key}";"""
            result = self.CRUD(text)
            return result
        except:
            return print("[ERROR] check update_wayline")


    def get_object_key(self, wayline_id):
        # wayline_id는 json이어야한다.
        try:
            text = f"""`SELECT oss_path ->> 'object_key' as object_key
                        FROM public.waypoint_plan
                        WHERE oss_path @> '{wayline_id}';"""
            result = self.SELECT(text)
            return result
        except:
            return print("[ERROR] check get_object_key")


    def get_list_object_key(self):
        # wayline_id는 json이어야한다.
        try:
            text = f"""SELECT oss_path ->> 'object_key' as object_key
                       FROM public.waypoint_plan
                       WHERE oss_path is not null;;"""
            result = self.SELECT(text)
            return result
        except:
            return print("[ERROR] check get_list_object_key")

    def get_list_name(self):
        # 
        try:
            text = f"""SELECT oss_path ->> 'name' as name
                       FROM public.waypoint_plan
                       WHERE oss_path is not null;"""
            result = self.SELECT(text)
            return result
        except:
            return print('[ERROR] check get_list_name')
        
    def get_oss_path(self, wayline_id):
        #
        try:
            text = f"""SELECT oss_path ->> 'object_key' as object_key, oss_path ->> 'name' as name
                       FROM public.waypoint_plan
                       WHERE oss_path @> '{"wayline_id": {wayline_id}}';"""
            result = self.SELECT(text)
            return result
        except:
            return print("[ERROR] check get_oss_path")
        
    def get_wpml_info(self, condition):
        try:
            text = f"""SELECT    waypoint_plan_info, shootphoto_plan_info, wpml_info, oss_path, waypoint_plan_id, wp_mode, area_boundary 
                       FROM      waypoint_plan
                       WHERE     {condition}
                       ORDER BY  waypoint_plan_id DESC;"""
            result = self.SELECT(text)
            return result
        except:
            return print("[ERROR] check get_wpml_info")
        
    def update_oss2db(self, object_key, template_id, waypoint_plan_id, filename):
        try:
            json = {
                "name": filename,
                "wayline_id": uuidv4(), #파이썬 uuidv4 생성 라이브러리 찾기
                "template_types": template_id,
                "object_key": object_key}
            text = f"""UPDATE waypoint_plan SET 
                       oss_path = '{json}' 
                       WHERE waypoint_plan_id = {waypoint_plan_id}`"""
            result = self.CRUD(text)
            return result
        except:
            return print("[ERROR] check update_oss2db")   
    
    
    def delete_wayline_row(self, object_key):
        # object_key는 json이어야한다.
        try:
            text = f"""DELETE FROM public.waypoint_plan
            WHERE oss_path @> '{object_key}'
            AND waypoint_plan_info is null;"""
            result = self.CRUD(text)
            return result
        except:
            return print("[ERROR] check insert_wayline")
    
    def get_kmz_info(self, id):
        try:
            if id:
                whereSQL = f"w.waypoint_plan_id = {id}"
            else:
                whereSQL = "w.oss_path is null and w.wpml_info is not null and w.waypoint_plan_info is not null"

            text = f"""SELECT
                        w.waypoint_plan_info, w.shootphoto_plan_info, w.oss_path, w.waypoint_plan_id, w.wp_mode, w.area_boundary, w.name, w.wpml_info,
                        m.wpml_drone_enum as droneEnumValue, m.wpml_drone_sub_enum as droneSubEnumValue,
                        p.wpml_payload_enum as payloadEnumValue, p.wpml_payload_sub_enum as payloadSubEnumValue
                    FROM
                        public.waypoint_plan w
                    JOIN
                        public.drone_info m
                    ON
                    (select w.wpml_info ->> 'droneId')::integer = m.id
                    JOIN 
                    public.drone_payload_info p
                    ON
                    (select w.wpml_info ->> 'payloadId')::integer = p.id
                    WHERE
                        {whereSQL}
                    ORDER BY
                        waypoint_plan_id desc;`"""
            result = self.SELECT(text)
            return result
        except:
            return print("[ERROR] check get kmz info")