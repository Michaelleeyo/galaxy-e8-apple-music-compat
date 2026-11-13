package com.e8.auth36;

import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import org.json.JSONObject;

/** Uses the app's original StoreAPI only after its original IdMS UI completes. */
public final class FinalAccount {
  private static final String P="com.apple.mediaservices.amskit.";
  private static final String ACTION="E8AuthenticationCompleteAction";
  private static final Map<Object,Boolean> registered=Collections.synchronizedMap(new WeakHashMap<Object,Boolean>());
  private static final ClassLoader CL=FinalAccount.class.getClassLoader();
  private static Class<?> cls(String n)throws Exception{return Class.forName(n,true,CL);}
  private static Object call(Object o,String n,Object... a)throws Exception {
    Class<?> c=o instanceof Class?(Class<?>)o:o.getClass();
    for(Method m:c.getMethods())if(m.getName().equals(n)&&matches(m.getParameterTypes(),a)){
      try{return m.invoke(o instanceof Class?null:o,a);}catch(InvocationTargetException e){throw unwrap(e);}
    }
    throw new NoSuchMethodException(c.getName()+"."+n);
  }
  private static boolean matches(Class<?>[] t,Object[] a){if(t.length!=a.length)return false;for(int i=0;i<t.length;i++){Class<?> c=t[i];if(c==int.class)c=Integer.class;if(c==byte.class)c=Byte.class;if(c==boolean.class)c=Boolean.class;if(a[i]!=null&&!c.isInstance(a[i]))return false;}return true;}
  private static Exception unwrap(Throwable e){while(e instanceof InvocationTargetException&&e.getCause()!=null)e=e.getCause();return e instanceof Exception?(Exception)e:new RuntimeException(e);}
  private static Object companion(String n)throws Exception{return cls(n).getField("Companion").get(null);}
  private static Object success(Object v)throws Exception{return call(companion(P+"bindings.Expected"),"success",v);}
  private static void log(String stage){android.util.Log.i("E8Account",stage);}
  public static String route(Object provider,String raw){
    try{
      if(raw==null||!raw.contains("AMSIDMSAuthenticationCompleteAction"))return raw;
      JSONObject envelope=new JSONObject(raw);Object d=envelope.opt("data");
      if(!"run".equals(envelope.optString("command")))return raw;
      if(!(d instanceof String))return raw;
      JSONObject data=new JSONObject((String)d);
      if(!"AMSIDMSAuthenticationCompleteAction".equals(data.optString("actionClass")))return raw;
      if(!data.optBoolean("makeCurrentAccount",false)||!data.optBoolean("canMakeAccountActive",false)||data.optBoolean("ignoreAccountConversion",false))return raw;
      if(data.optString("username").isEmpty()||data.optString("passwordEquivalentToken").isEmpty())return raw;
      // Nonstandard request headers keep their original implementation and semantics.
      JSONObject headers=data.optJSONObject("additionalHTTPHeaders");if(headers!=null&&headers.length()!=0)return raw;
      Object registry=call(provider,"getActionRegistry");
      synchronized(registered){if(!registered.containsKey(registry)){
        Object factory=Proxy.newProxyInstance(CL,new Class[]{cls("pi.p")},(p,m,a)->{
          if(m.getName().equals("invoke"))return success(Proxy.newProxyInstance(CL,new Class[]{cls(P+"webcontainers.IWebAction")},new Action(a[0],a[1])));
          return objectMethod(p,m,a);
        });
        call(registry,"registerActionClass",ACTION,factory);registered.put(registry,true);
      }}
      data.put("actionClass",ACTION);envelope.put("data",data.toString());log("final-action: original IdMS complete -> original StoreAPI");return envelope.toString();
    }catch(Exception e){log("route-unavailable: "+e.getClass().getName());return raw;}
  }
  private static Object objectMethod(Object p,Method m,Object[] a){if(m.getName().equals("hashCode"))return System.identityHashCode(p);if(m.getName().equals("equals"))return p==a[0];return "AccountAction";}
  private static final class Action implements InvocationHandler {
    private Object parameters,context;private boolean started;
    Action(Object p,Object c){parameters=p;context=c;}
    public synchronized Object invoke(Object proxy,Method method,Object[] args)throws Exception {
      if(!method.getName().equals("runAction"))return objectMethod(proxy,method,args);
      if(started)throw new IllegalStateException("Authentication completion already started");started=true;
      Object given=args[1];
      final Object continuation=cls("hi.c").isInstance(given)?call(given,"intercepted"):given;
      new Thread(()->{try{Object result=perform();call(continuation,"resumeWith",success(result));log("final-action: genuine-account returned");}catch(Throwable e){try{Exception cause=unwrap(e);log("final-action failed: "+cause.getClass().getName());Object failure=call(cls("bi.q"),"a",cause);call(continuation,"resumeWith",failure);}catch(Exception ignored){log("completion delivery failed");}}finally{parameters=null;context=null;}},"AccountCompletion").start();
      return cls("gi.a").getField("COROUTINE_SUSPENDED").get(null);
    }
    private Object perform()throws Exception {
      JSONObject p=new JSONObject((String)call(cls(P+"datastorage.AMSAnyMap"),"toJson$default",parameters,null,1,null));parameters=null;
      String user=p.getString("username"),pet=p.getString("passwordEquivalentToken");
      Await auth=new Await();Object value=call(cls("Gb.b"),"a",user,pet,0,new Completion(auth.proxy,auth.emptyContext));
      Object result=auth.finish(value);log("StoreAPI: response received");
      Integer status=(Integer)call(result,"getStatus");log("StoreAPI status="+status+" error="+call(result,"getErrorCode")+" account="+(call(result,"getAccountInfo")!=null));
      if(status==null||status!=0||call(result,"getAccountInfo")==null||call(result,"getPasswordToken")==null)throw new IllegalStateException("StoreAPI did not authenticate account");
      Object stores=call(cls("lg.b"),"e"),accounts=call(stores,"a"),active=call(accounts,"activeAccount");
      log("active matches="+(active!=null&&user.equalsIgnoreCase((String)call(active,"getId"))));
      if(active==null||!user.equalsIgnoreCase((String)call(active,"getId")))throw new IllegalStateException("Authenticated active account mismatch");
      if(call(active,"getxToken",call(stores,"f"))==null||String.valueOf(call(active,"getxToken",call(stores,"f"))).isEmpty())throw new IllegalStateException("Authenticated account has no token");
      JSONObject tokens=p.optJSONObject("idmsTokens");
      if(tokens!=null){setToken(active,tokens,"com.apple.gs.ck","setContinuationKeyToken");setToken(active,tokens,"com.apple.gs.idms.auth","setIdmsAuthToken");setToken(active,tokens,"com.apple.gs.idms.hb","setIdmsHeartbeatToken");}
      call(active,"setIdmsPersonalEmailToken",pet);pet=null;call(accounts,"addAccount",active);
      Await conversion=new Await();Object list=conversion.finish(call(cls("e7.e").getConstructor().newInstance(),"getAccounts",conversion.proxy));
      Object media=null;for(Object item:(List<?>)list){Object identity=call(item,"getIdentity");if(user.equalsIgnoreCase((String)call(identity,"getUsername"))){media=item;break;}}
      if(media==null)throw new IllegalStateException("Authenticated account conversion failed");
      Object internal=call(context,"getInternal$AMSKit_fullRelease"),adaptor=call(media,"getInternal$AMSKit_fullRelease");
      // The original native completion saves the authenticated account with Create
      // before setting the web context. Keep that account-provider lifecycle.
      Object provider=call(call(context,"getAmsKit"),"getAccountProvider$AMSKit_fullRelease");
      Object savedTask=call(provider,"saveAccount",adaptor,(byte)1);Await save=new Await();
      call(save.finish(call(savedTask,"await",provider,save.proxy)),"getOrThrow");
      Object task=call(internal,"setAccount",adaptor);Await update=new Await();Object updated=update.finish(call(task,"await",internal,update.proxy));call(updated,"getOrThrow");
      // Finish the original app's music authorization before resolving the UI.
      // This is the existing token provider, using the genuine authenticated
      // account and the unmodified StoreAPI signing/network implementation.
      Object tokenProvider=cls("B9.h").getConstructor().newInstance();
      Await music=new Await();Object musicContinuation=new Completion(music.proxy,music.emptyContext);
      Object tokenTask=cls("B9.f").getConstructor(cls("B9.h"),cls("kotlin.coroutines.Continuation")).newInstance(tokenProvider,musicContinuation);
      Object musicToken=music.finish(call(tokenTask,"invokeSuspend",cls("kotlin.Unit").getField("a").get(null)));
      if(!(musicToken instanceof String)||((String)musicToken).isEmpty())throw new IllegalStateException("Music authorization did not finish");
      log("StoreAPI: original music authorization ready");musicToken=null;
      Object jsAccount=call(context,"makeJSAccountFromAccount",media);
      Object output=cls(P+"datastorage.AMSAnyMap").getConstructor().newInstance();
      Object anyAccount=cls(P+"datastorage.AMSAny").getConstructor(cls(P+"datastorage.AMSAnyMap")).newInstance(jsAccount);
      call(output,"insert$AMSKit_fullRelease","account",anyAccount);log("StoreAPI: account converted and context updated");
      return cls(P+"datastorage.AMSAny").getConstructor(cls(P+"datastorage.AMSAnyMap")).newInstance(output);
    }
  }
  private static void setToken(Object a,JSONObject t,String key,String method)throws Exception {String v=t.optString(key,"");if(!v.isEmpty())call(a,method,v);}
  private static final class Await implements InvocationHandler {
    final CountDownLatch latch=new CountDownLatch(1);final Object proxy,emptyContext;volatile Object result;
    Await()throws Exception{emptyContext=cls("fi.g").getField("a").get(null);proxy=Proxy.newProxyInstance(CL,new Class[]{cls("kotlin.coroutines.Continuation")},this);}
    public Object invoke(Object p,Method m,Object[] a){if(m.getName().equals("getContext"))return emptyContext;if(m.getName().equals("resumeWith")){result=a[0];latch.countDown();return null;}return objectMethod(p,m,a);}
    Object finish(Object direct)throws Exception {Object suspended=cls("gi.a").getField("COROUTINE_SUSPENDED").get(null);if(direct!=suspended)return direct;if(!latch.await(90,TimeUnit.SECONDS))throw new TimeoutException("Account completion timed out");call(cls("bi.q"),"b",result);return result;}
  }
}
