#coding=utf-8
from nose.tools import assert_equals, assert_list_equal, with_setup, raises
import ssdb
from ssdb.connection import Connection


class TestConnection(object):
    
    def setUp(self):
        print('set UP')
        self.connection = Connection()
        
    def tearDown(self):
        print('tear down')
        self.connection.disconnect()

    @raises(ssdb.ConnectionError)        
    def test_on_connect_error(self):
        """
        An error in Connection.on_connect should disconnect from the server
        """
        # this assumed the ssdb server being tested against doesn't use 1023
        # port. An error should be raised on connect        
        bad_connection = Connection(port=1023)
        bad_connection.connect()

    def test_init(self):
        print('init')
        assert_equals(self.connection.host,'127.0.0.1')
        assert_equals(self.connection.port,8888)
        tmp_ssdb =  Connection(host='localhost',port=9999)
        assert_equals(tmp_ssdb.host,'localhost')
        assert_equals(tmp_ssdb.port,9999)
        
    def test_pack_command(self):
        print('')
        output = self.connection.pack_command('set','a','hi')
        assert_equals(output,"3\nset\n1\na\n2\nhi\n\n")

    def test_connect(self):
        self.connection.connect()
        print(self.connection._sock)
        assert_equals(1,1)

    def test_send(self):
        self.connection.connect()
        print(self.connection._sock)
        assert_equals(2,2)

    def test_response(self):
        self.connection.connect()

        #----------------------set a hi------------------------
        self.connection.send_command('set','a','hi')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('get','a')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','hi'])

        #----------------------set test 123------------------------        
        self.connection.send_command('set','test','123')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('get','test')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','123'])

        #----------------------incr test 1------------------------        
        self.connection.send_command('incr','test','1')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','124'])

        self.connection.send_command('get','test')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','124'])

        #----------------------decr test 1------------------------        
        self.connection.send_command('decr','test','1')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','123'])

        self.connection.send_command('get','test')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','123'])

        #----------------------scan test a z 10------------------------        
        self.connection.send_command('scan','tess','test','10')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','test','123'])

        #----------------------rscan test z a 10------------------------        
        self.connection.send_command('rscan','tesv','test','10')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','test','123'])

        #----------------------keys a z 10------------------------        
        self.connection.send_command('keys','tess','test','10')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','test'])

        #----------------------del test------------------------        
        self.connection.send_command('del','test')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('get','test')
        p = self.connection.read_response()
        assert_list_equal(p,['not_found'])

        #----------------------zset test a 20------------------------        
        self.connection.send_command('zset','test', 'a', 20)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('zget','test', 'a')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','20'])

        #----------------------zincr test a 20------------------------        
        self.connection.send_command('zincr','test', 'a', 20)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','40'])

        self.connection.send_command('zdecr','test', 'a', 20)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','20'])

        #----------------------zscan test a 20------------------------
        self.connection.send_command('zset', 'test', 'b', 30)
        p = self.connection.read_response()
        self.connection.send_command('zset', 'test', 'c', 40)
        p = self.connection.read_response()
        self.connection.send_command('zscan','test', '', 0, 100, 10)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','a','20','b','30','c','40'])

        self.connection.send_command('zrscan','test', 'a', 100, 0, 10)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','c','40','b','30','a','20'])

        #----------------------zkeys test a 0 100 10------------------------
        self.connection.send_command('zkeys', 'test', 'a', 0, 100, 10)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','a','b','c'])
                
        #----------------------zdel test a ------------------------        
        self.connection.send_command('zdel','test', 'a')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('zget','test', 'a')
        p = self.connection.read_response()
        assert_list_equal(p,['not_found'])

        #----------------------del test------------------------        
        self.connection.send_command('del','test')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('get','test')
        p = self.connection.read_response()
        assert_list_equal(p,['not_found'])        

        #----------------------hset test a 20------------------------        
        self.connection.send_command('hset','test', 'a', 23)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('hget','test', 'a')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','23'])
                
        #----------------------hincr test a 20------------------------        
        self.connection.send_command('hincr','test', 'a', 7)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','30'])

        self.connection.send_command('hdecr','test', 'a', 20)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','10'])
        
        #----------------------hscan test ------------------------
        self.connection.send_command('hset', 'test', 'b', 'b2')
        p = self.connection.read_response()
        self.connection.send_command('hset', 'test', 'c', 'c3')
        p = self.connection.read_response()
        self.connection.send_command('hscan','test', '0', 'z', 10)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','a','10','b','b2','c','c3'])

        #----------------------hrscan test ------------------------        
        self.connection.send_command('hrscan','test', 'z', '0', 10)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','c','c3','b','b2','a','10'])

        #----------------------hkeys test a 0 100 10------------------------
        self.connection.send_command('hkeys', 'test', '0', 'z', 10)
        p = self.connection.read_response()
        assert_list_equal(p,['ok','a','b','c'])
                
        #----------------------hdel test a ------------------------        
        self.connection.send_command('hdel','test', 'a')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('hget','test', 'a')
        p = self.connection.read_response()
        assert_list_equal(p,['not_found'])

        #----------------------del test------------------------        
        self.connection.send_command('del','test')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])

        self.connection.send_command('del','a')
        p = self.connection.read_response()
        assert_list_equal(p,['ok','1'])        

        self.connection.send_command('get','test')
        p = self.connection.read_response()
        assert_list_equal(p,['not_found'])        

