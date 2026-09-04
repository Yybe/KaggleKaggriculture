"""Pure-Python standard submission for the three-day shop router."""

from __future__ import annotations

import base64
import copy
import json
import math
import zlib


_ROUTES = json.loads(zlib.decompress(base64.b85decode(b'c-rN?Pmg3*lI8bZxXuN`<4<O4$13`C5zVS3SmZcHg+QSJjUYf6En3<M`tC|*M0mJAJNC0<c3&{r(<=s&5$^ZhcmJ3jJLlLx{_&6h_nZIy-~Ro7{P%zV=70IeH$Q#%_rHJh`0ktk<KO<T|Ly<&{12ah{2%}J@Bin2|9?LJ{Eu(`^y`27=TAR>`u^8H|MJbdZ%%(Xe)svmH@A<E|KGdI5Bb}tpMUvF{waSy{`lkTpMQ9K_w>PkKOVn-{pa_afBx(7$4`Iz{AGvV{{1gM{Cxbz{o%I{`R;E&{PnxvzVy$ZPT#ycgn$0~UyjG0e)}JrCpjJe{>$Zqe4d~m{`{}M{`CAwzkSa0ue?6>#XnvDGR?wG{mrkRfBx8~VPAjw>ra3B^@kt7|L5m7`pd7sO@;F+x1;#!$M633%X#*%hO_zf%V9lz+Vx<>m_L8`pO4<;ymJS9`tFzG&zm=P`8E25iIM;LyEtd_QH7WJ^zrZHG;ZenV#H5B>@+BNx33HMdG20c+RFsT_5OBm@b#Pi%WsFl)s)2f+jTU@@4^8PUeEbm!nAGv>di)%zn-hvd-|=NM)CaoYW;{oY-Ve(#k{$<)O)(v@6Z45b-Q1_y6i=joBDO~#U55KCccLH1)t9X@qytd_~_Lci@&}3oi~`e@YCwlJ^#|>`~Na6qj`IsoAbx!({}MM)i<us*3)=;5B2mfa<b0<Z!%fee+x6R*XLhM*1qFTexQ%t#u-V3T!yvv3OQ~Ub_`1EeHsFJ87hg>zCM1Q@1l!OKHpC2JbU_|@OkkPf)MNVb7Ppd{oGGK{&@WJFaP{6$De=s;m05T*KKSf|3Ahj>MvU7*h_SgedT#Q{{7Rh+qZDOVlVy}?%9yqJ%40z*}wdj9_zw*?nDq9=fZeB=QH7Ts1T2MgFDng$$3pSbC2?aUoW!P<A32w`~K%oKV6^s=iRw-c3wR79!K%cCwtsLf1ttrv8Qg|(BMDQ;3iSTzMpn|{(L@S3*0UohAs$q4e;GRmJtC2G4ZhWlTt5U*(Rgmbgv=<k^6Q6BoTYzC)OEJoM6Zttue+)4&!NNZPlcTY=m&AGEP?aW@EUpX2r`|TC{3><>ytiNrNpPUc`bI(Nv5>{_@?=|Fs%%oY3<d60gcf9OBHXp`J&$%UXT?hO2mZlkC>Jj8MMWvK3MD)wwSh#CiVZdz9D1ovyz`^zOQ-!sD2{esP$po#nrK^??Mv)(Fg1m4e4f30}GGAyzOJ&YOlFw{t+G8Edov6aV~nLKy2_sDqDIc+<Fn?4U;dwEgP!4K#~OylYt;os*D<hkbda7@uxmDQfhhtTBPf^>rAJA?H4)gEt*6RUUe8T}%>8Ve7T4_*2fDaYz?$T|_<<QH&xt3bVr3u70#YHD*D}ZE`rpZ=$GK#xA#J>{0^6FOc8sE6bNo@A1oMQ?2zFi6oi553tKX_Zod^78y1H&O5=o@xP#YL+4LAqn;L&K8Um?pKF%Tt|%^>Cu)RX_e&v|ioCA>`SUFO{7DrSet-1mErOyn_Ui99u`NXPfWPNr;{X23&)=Q?bo}|}|0cdGPX6o0Gb6A;#3~-A6^XgGrnnaBPbdDJoc<;FP2IIlcm<OxLXaL};$lZJ0O6urFL)4f=XTvph>f)3&#NR{pUVK#>%S!+ipjWgV~$HAimDmIa_~+mNTkykY@hd~VuW38Ywz>+dR1$WA;<ync?<IoUv!R|8o-YT<?rXP5@V0z;ohZJ<L%?`ig?}cS!|2Z*WDcV!r-sooUy35cR(lTLf*4%<CJ%PoMfN7i{O~xi|Z?O@q4-<N#moNFKoxSPlc7?PMTC*N-oh}L{*I*3M8>pSjeX9mDuwf3ta2~_-A}VCQdm!jj|sAZk?k<eYAeFDhX;-U(KSEc!v7o7oRNxSW(Y(mW+^KY^4MF!syjdK^dds=WH<^`%hHv=FvNko0)*sEvai-Y|mpoi(j5=rb0lazA5J!a$qLTfkPwwig9P-ncs-uy<N@=RZJ(oJ0$4Z>QPH1Z}Hw^P#b=&8Qi*Ke?4p<_`EH~FDUZ);OlJ}HEQuI%in>ol+P?QXyHp0`PlweI~)=penGeI{*4jXoIZW}yqIpjbvW|s$y54AF`U;-;yi#hVVq9F=l}Ql#{0g~F~5E?f;ALr#%n54zq8+&aOQEKIUgvFMLa@;zjhdKO7c%NJral8ma$$3U2P3`hH-=&$0bB;VyY?sa3Q6wGDa@TD4&V{BI?T-%dT~><csf$op4oolX7mU*2!5Td+K#!hJRj@Nh}?ASfw}0CG3|Uy-UTpirGQ)h3Zcm7(Gl7HIV}Jxaj3~s$3~jXk^w@Fo;$}y_Q;^Sd$$XMWuKVF`z^36w76Gs_Y_lp<FhES?W(P-c+0_u`*K~aSAL<(*3Re&LZ!aH~RCQ{b-076LOI=?J1XO^s401cyMe^UdEx{jhIXOC3?rTD{j7unh$%X!-On!N+BxFF?7#WvTu;dPE|6S3<VSR-mkBaoP|+KF6Q39{&PO>&;RfILs}HrqtNjBE&A*~|KjTpRj|KbK7JYRsW2}4GyTtHUTwlX>#1v%IOUlZ5;6T4yjf>SW)5j5$=@st`*wT~k-GoPJ1jDVoLjsH^CV_v*;XL%U`@k7#c29g4*z<woU#B&Hv`u@)_8KKqcP3NlTRpXI2RUuZ(PLnXz!ct;?0!t4(PcfD%J>8Ct5oY+4>7#tWV0;XA6P8L`~AbMv2l)k?;U+H7IEzg(IKXqLOA_hxt?(l(*dsFGK?L8W5fTC5?67)R-#%AOH*hD?QiMk$b~1=bDx4?p00k&WH1x&w&G`@*bu*pqg$$`7c+-Uw`=VU%z?xpz{x;o#`|8`a}7)Ij^0k-``m9COEWF+1iGnt|>1$mQc(ipe6y{)Ci#g6W<y|b^)|sd*nXN6xLI*G&9KL#Yz%iu|5!Y+Uyd*Hnj3az3hKt3xh%yt{in0-pO<%yKXUCkWx&NW=ii^J3L#6gM<OaG_71~_hrhjlVCYBQ`}cMB?*v6M=0!>YPj<Y=+9M#vfWw7PTkG->TpbIL@1ZRp0;W0d^zSqV0|x=dry-GUaU2b6)sA1)p_8*P7&l$<&c1N%(E;BdRAu^N2G@#%YA_BVQ;^xqXjkbge{vfr3Jo}43{{X$_>%BTx}VvVuVl?AF#OJaQ-PRqsqcJr2S0#ZY#f<YvWb-PZQm6mR_d{cZ-|vmf6Kp*;R9cpEi-H_mZi8OSQ$6;ce=8vs`5Y#%}yy5N0f!3mY*}EOy3myyhXXAIm_NC#sM|iBk-zpeEV|1k-t&mO95j_0d#|xr?QCE_!s-=$(})WJ6X?oRhMev{!)0E?9#_<=l2>SV+EmWq2%Dh=1xZ+C=Syh%qX^!G!RdxBr1S^&e`0F&_C2=KMMz-U_7xri0;L#a(!0Yf{!odOA-aiA!l0OF&T&OF?hJX;-!zxJF?#3p2-PN~A6eMo1%0m&-j$Ipk{h7n!dcg2kVvWW{Dsy2sR7uAhm~E9@_RZ^4ZS2FT(Q-v+W6KW!nRLrnFmiNi^mj0HJB&$&uW-_*`@<|e0D6=)8RJS3AO#duDldJ`!Je*f6eflspGJ<Hiig1k!-yi1#<+J?8Rkrfo;%PL`><lc^m&%MXkH?O}<qrUq^61V$PO!hlX2ATo1`;#JvsCi#-MU%k;7b9H?U2*|j-tgO8wS_xmPAO{4+3%9WO5r=_7p#N@9Hwfl#2s7hStG<yTKpOjY#lp83N8wJ6SluCAfD&u(hp*eH4*0G_w~-Y<3ssAV~@XnvSiMQ@md7(%Rf;6mg#^u@i<jCo<Htz=bzpRT^55=dxIYlFxm=sG#>Hh(1FPnsKxIQVu>g@LDL|A!QM}(dS!=i%SF}z;4VF?t|yM4cGSF3JfwOK>MB_tJShxs+}hr&+DLBy{3%#l<4yy2S0%hEBsipVoV+YzcR4M0MNXU=OYHVWz_@^INqnd#Jsxa^>2KstaU8#H>GPO{>YoU9N{~=IgiA$rQrXDI&V3Fpy0+(wN>j`1Yi2WhEhafpiwc>q@M<R5@p?jf#QT5+Mc%zNy~zZ|5>spuyoF(I9|yg>9WaBS4<Y{Sw|AXjD|$3NwdWd%A%sndLDH?37Tnwn?9D#zjPP(|>_8!Vc);aGP(!8zmkBDeX=x~ez>wnb#n^G#sj0&vWfbFl#E3eQJr!kzi)#G9J`o4FDqI`map#dVDZ0APeC?vBviZA;S7J72*hCT!2D0c^W0RqS!Zwq>CGpp&G--9T5EZ1s^3PGrp_JI(Z`HCxQU^PFOs8378|6}|ovw;)kQ(|7k?YbT8OhqE7gerD--%x%@{jUhq9$vit~+Y$MJCbQK}3uo68~Hs%I>oaM17HbRO5v|U7Tz<(;C?b3AefR;L1ruDtAl4K-v_OT{EVl)K;*CKVg34s|D6-t3*vP)6SH7Cw99dq3UW@&p~cLP0Wa=kxS-ic6tJnzQ}|)mA$QGJ<56eXpfhAw--x;?u&+RxwkUK*yy&X_T=U@w7mAHyCY7f0Fc^u!&Yh1G{JXpo~Aye@v7Sdn2%q90Araq+&91h&``MAs++rBg@h!CmbPP1Y%hqv$F!h65NVLUvApH&aKL$8=-__WbeG@$u}!mKMe>G#-m&~5b8-}7H0b$qDaX~c-CKu}*e<n>lY87=TMgzhPypJU5~_uTZ>r+#_(DpBp2cGaYduD#GyV(G1Y9gEj?dtCG4!(5W87YJc07)H8rQYZG48EKjGTR7o;SJ{og9Hoyo>h2K!|5-zgQu9w3PRLLn<ti%}@e;oQ&FLRrs9thjuLBJF^D}qM(jvhm)Sw2J}GgHn9#(b##RWjvN{7WhCl2$O<v8oJb)k#?V;Pd98Wi%pONdvWS=>);0Rw%I-VM9o9O-zSkA>k6$?vTvQ75%jtub6c+Ci^1=ErFdKG>D;NDoQnK~FO-;pdg!V0F)IThQD+s*|;9MH&+P#vO5lcE>9^wt<?u77bFE>C1he*HgPXu7Orm>l-_^EVI4bg_ljowq!%$k;3ioaA6{e3J*wd6)H2U^C|og}s6>j6<Xac3HUMV-XDo_1cgT1lRAhH=a1PC=#Orl7#y2)0{}V^ruw@pW8(jj1VngZTa0<Du;%WR01N>x~^VXWh<^ea8Y=Wq>ZrTZ}Bm%5x5u7P_6#r4`F>Z@<RS$VAa#a)P#@9)N^R1s7#ZU{|PVBA4<^JTxgCjXzB0uQ1P<rJqLf`;us727h0_`X~ZkiDjjf?fa_npRcDDN%%*wMQ2PnCezWN9n%KnF&7GFjIrKLd+`*+Z*ekZ!xT!-FN3??{LfJEf(N_p00pfKgo5uVz1#ZluN7s$_D>7@^4W|q38-t5IXzEJuRo?H<Xx0{ACd%DkO_m(W>emMFv>I3_v&ImF!?8U(Ww958GRF-XsqGmilbb%5Y)~`$8m+liwBHLbzFp_L`G;b$aD!-Wdr{*aXD==vAX^m%dKI;KrL>Cv(=6ZuWA(FsUlk4((IK-cIzcILT;@k*Ahx{M7rkZlPO%bjKX5}qZu70LA$xkMwm72g&bDfW$C3hf0bW*nq>~D2js9`v~TlavROxS&<W#Gv;gB8%<-C?$IKq}_&Hj(+FjeWhHtD$GR|CL`wq3%=Fs;n0bhjfnR@znF8&5z!h&CTY<7(*B+@$JzUwF<BX|(K9n+-qzW0x{w_XW4ydOOqwSI}l3RlN4^GXNwD(qB8G&Ha?Z8e{g(ZuVGUajGZ*JIQB8namV^j#uEmk-hiKgj-Wb#`sEN+4an`Os?lI-5EOiD8Y>CQPj4udmrCY9J{P;!wjCD}8RV*%+>f%cSCJ`j4(^(C}@XuL<sy6=y##+cFzo&DgHz?fW18B|jNqxgrc>w`{*@DTdX4x_lPUdCeCxkc7s{){zma(TTn}$ZBm+^dauu=)w17!F5mF9iDtJ4I{7nOVjL^Kb;(Sv<u@pKh;oAkD`OIZ6rK3yMDk!P8d(w71yBy5OAA{b*I8$F{ctILn@`$nzF+e^Mo03Cy9%REQk$`)}<5Hhh(&xDx|`Ls+E(c8Gzg3dbpjH;7TbberFXSVFdG9<Sq+(Fi7c*TjA@M^$GSUJ-JQEC+FlFyZm*;;ilts{0icj<amTA($9$@d&+#Tz$O*zef!ujwt*kwn*{;d=qRUw#hPB~EAQUrMl<Dhrhm*c8=|)~LeCt!?wM2czglm2l;^6M9jb%fW(=h8zHs5y@zt8rPZZvKrLupgi(qpSV^S7g75*E^e$se;Ew1yM?_H<W8a%v+|703AsRMb@vME|Gbmv3up@>ZH(i<M?YuP~@7nt37)VcOTn_Z{ja6AYtYbq>lw!jSV9BVPL%daomnusS#!RcdPw+{Wsu`LGCIk=0Zf3j5UZQ@UCK$H*ZZiZq=!fODa`Q^(RbR=r{LcV{)W~a?ObI0Xfh~|s-@UFw?HRK=oeQ~)n|2Z1DUmRvncHA-YB^8g_N@jW=o2FD71Q3)LSi5*Du^j??G1f2(u=PR2C>=#BM|RNuFKOC+!h&AGHuFJrFI>?@5C`KbmHybKZg?}h$%H>Xj_DhJ4C^-R8y+PQ8(oMk?ytfBTf_W*%<Nz>$dH!dQCDVsh)4{;G><&%O5#QXm$z)KiFaC5LgJ;h*7?2cGGjN7ZZxbSa=7hY`0eAA?crEf`Fxg+nAyVAVw`)O0Tdc?gUQ}Wb_)0hB5St_0m5Di$QxD9dEI+OYcAwVP3mYOX+m>FT;^sfDNmjjovBzgMEIb=*!J6*Frv3NIfaz#gpUft@MLeJ@CxP0V7PMkpjXArJ=`mfS8^1vBBPDmop_1IC0e}CmsQ$2%oZ)!V(yo(Y|J-MKCTxCIpL`1yH-YwTNU>fH!jVRTGpNTMngtV_ga93Xa`=K$+bF2DwU~WvR9+(jU1Q82X2L6f7kP*SbOERpCOrYkZ2_uRyNBFza38cP-t5j`nD8k5Ro6u8Z-OWYFHQ^{9%ViflZc)9RI_AEQloH!vp~2z=)-hDAMzL*O%eK{`~F5F$j34NXuOf5<!1EXZK^`;9W@s?4Xi!%j20R50oIFSK#YqQJMfJjG;+op9)N6y^1I-6LxDw*GK!sD%J3t(O!lXF}m!yXK>gk<CrAhad^mS?;X2)!$ZY(R4=0txmW9&&*DQ_X45Vj=FGDKU+I)8uS7u>T6T%Zi7AEYVZ&5)O_Y%FIw*uKLph>n&8IvD2$nyBEFvR;tV8vv=e#HzlXt&B<-yrRh~m?YxlW)!P$ggMc553h8hi5G7{Q+qZ{g$8iCV~4da*&`36{(WfaTf&1~I!iw8<q8>i;B*4(T)YI46uBWV%OjLR+Q|mblblnppnEF)H5X<6fhfVnb^0&*kLWKX5RJ6oCv;LV!22qh3`=A+jU6bt0A_S~^p$TC-eEch%_#H9RU^csA6Vp_Chl@GxmwH0=P5sZP7W<R3^Mv@sV!9C{%A>3D*gaLt83;6C8Ys;GvHH2{Md-NYwL#nJLxfojg$Sh>thGMh5EvDxTjqp=ZH1s}!WG&PKIMG#Cjo0S&`%RgW_W6soXFW|}Mvuu+~@TOL1Xu-<Oom+gDJ)9RNUB#-TX-0ubN_tCy87-U*-jVh*B?$u}97WsnP(_%czLB(;0h5lb6JVhJ>8O^mD$o@0oNu2~V?xaadUAPIn6=Up9es1e)LU_k?fFZjmQBWZ#)qw|WfD^a+*ic?azdKXk`RL}R0Newj3O&o0Tm}69a7|eufio?)?9s33&oLZMnT}L7{Ve~UCSAeV8rT)KITE>2)RJTO(R=u82|MUO4<YU!($P@W822mu%2us<7br1SJ;|Dk-_iiZiWO*<jCbYwyA4AGd>y;HAZRJw(CPmXJTkasy7WHL5-Fze@HeB#l4PSEH`ff6te}~9NxrW)?yMFk6`(<LNQ3fT&+rB-tfV<;(&wM7fMy&d{#kW`_hK%MA_hDg=g(Mm?srZol`cQ5C%w&S1@$J8`OC80H};9_fYTEmYGMv4IvR9@+Qg$In*Tw6tju=qJvPqNU*U{LS1JpcD0<{>tVJUVy*&MRLC3JhSp}y*s8kdXrWTpi|^T^wjQs8ss<mgE}b>45ONeiACXP)3{aNveeo4@Z?dh|TGPgXUyxx9t^2zQD)fuz*)o@VoijJSO?*tKp!^AZS!_kCMGm$Us&%$;!J}sowy5%3TMN2R&ECR=U$R_C^G4O)&DLJ==jl&bPI^(3S;IZy;RmD^lJG!iRr()Nd2P*e3Yl+~O%0fB)t1MT9@J=;Zd$2Tu{s5s3(MSL){IgL)XtP_*#YH7MpvmtDm3)9EbrF!lv|e5AJHR5N_kA1THkZ`&`wG()yMld^jcy}Y(Pm|*qn$n!ww>3EgLRUV@S-k{oz3yS|f@r3-<GoJGwDBw|fz0Sfrmn!~lh{7H?s%qRzF{{Ft)NH58-0+#z_hn)c)%$r?SVvke-gPUkMRRO`EM3->3oLakL+t9p73lVsk!MXeJabp1qUw{f%A)69^iznUBVDkDD1B*PO3Rw*RZeKe9VoJ3KcOrkz%E}<7}mr?X2Iu<<x_y#MU+P)7OzHKt|SGYR&h$@^}*Ug`Z*W~4ZwUb1CY0dnI6vs(J5RFqG^+*V1>|qC`vNx+oTjA`&Va-)oc4-g(QeKW!7L{*5B)zP2LIE0Ud!4;Z)AJjH7ZEGGal|oCLM#-o-WCJLHrORsn(9!DugW3Z8dGb;d$uF5I!KXSlo3^SGwyY4XKKi<=M?lG)`KQ@oN-w*grT=2O}~@h%;s`uUmf<GuxT@c^c(3uP$$LXxnr_Fr1XGd(zd*)f_#j)7jWymnp8<rah=%xa|XZ|_Tt4_76#f__%~RO@A{mX!o*;r<F?#U&3t?Opod4FU{IAXy~<_L73mAhrq5h;9Y4x#Tv16Hz?DVJ9h3f$YNlRAmITU7x5r9hHbHV&6`R5-a-wR}U}xPt`iUbcNAfNq74qyY{maX^>E1L|>sH&xyg=I?6(7Q(^|9lAOGYh4qna0fU(<)WvhaOcX;Zf|3S=pLDF-Vu>SfMCjQ397QHtfpRpw1ncF3*jxz`$MXZK*=pmoZehC`=ki7+{5DzkFX#{sDZlrq2US;1-8i;^P-0+<hh3*@^@I=3%@+K0ymCr6q0f~zt~e&er~hsB(L<2Q@4@Im`;#|#`&g*lzA@f}FvRHqY`jr&}4Om4D{$9FG4$Icj0o0N0kalY|rHmzYV38MtqjUKh-bCK{pbH*vdOvB#^u23owtq!+&+O$fo9?QtEh;c@at~>(ysw&dvP@$M#u8Korc_(nvgs&f^HxR;iNG!0Z#S74EV0~U=pQO{s%P)I|^$k!72rU{bKk|~R4<Y8<)Oq3<hb2?Tv&z~MNLti07o%N~dxbqPSn@?GZ1$}7@ET_e?7!mOK4!*JkgsUeX(aKNx0SL?*)bX?&6t1y8OwptGR6zg<P(((UX`O@N(v@jg&23Nv&xkXT0Mnr5M_>>u1}?bu190-_%2ne+rh8d_PVc7sH|hQx{>qtcQCr(<U#F+2gxa1MB3JasANP!C>Up@11nrfStp@)+)h4DvQd_?hB~`?u&oj?<vgUI9CjgX9$4A5C@%I&5Z+DD9c%xdPo4W3uE@iCjg-9qT^)lTY7B*e1=CLkeczTrmkzNet{!N`+w__&U59(IUMwPZd#Y-}N`G*P)mzghB2~G?2TgbcL>g#V1{c<;EmWeBKALaC7(e8?W^Z7O@r+Ql#VomS{1$-GN7JB}Tw~(@OYn+oL)i}w&uKy$O8g+i!lO-27RcCxnBtd?!QFuKG^Y@(I#yP61gjUYj+-4$lw7kJFep#Aghf@Lj9pjk=L*h;&dn%$2|<GFm=-TMU+3!Dc!etg1_+NK$M0yxnipoQBs3IdUSld(lgjxbdepb1%^?letGfeDwb*BIr6e3QS_m%>;Z6Jq@QX`Z@ovom16SBumOG>MZ5;Pj^EjWRJTn(x@%6wiNGdTm{Ij;mT8r<d>7AlD6(MSBXuHF5fwmN+TlZGR$e_sz(CXH0R1%1gM<94Qm!L1{s>T>04{Fy<eGLcJ{`)JVOvjoM%o$Q+ZZl@ggT{Mq-hX9kOx>#bP-}vfh+qx5F=zxQX#86kB@3KBF&R$Lojwtw0*2!$NDZmzY&MORyFLM6L>Es<zfTc`{(3LfYok2%mRnT0&*aE2Nss2m^1}&FTu*JS&~$}U!%<TyAxgwvR&yJk!yuDT8W}_MvflV|Ret`{pFdeG2-a78DNBkZk9eaq&1zy3*jdaYTjPs4h6l5@sk^+L*a+8qE<Ndl-IPuuqq|}mMGCu`<bBt%E2MO-E;1F+E`3dzkW$L&nEcQ)DINzQ&_lLq^c&O3p&wMyjtqNJf$!PH;`Lol&h^?UB<}Ld@`b>jGN=CDJ6We_BeqIArd8^jK{IZ)7R1Aq%LScfJJ?>LiX{^8qA}xjUF)_Kw?6;c4x3KgC`?-dzSGFg&fZ>q!U}GKd<ynyda@f3vOm-jIuyO7D@+M>`kuPCHFpIH^OYIQTd9GP9v@6ak&fy)2d?M<HB<k1USn)YAY#&ner5%7;TW#rRJT3g$5D?MB$ZGzj5%qG^yORnsFrUinR!-Wd8Fv$O?s!dv3c=)jhLQ*mf3j)Y4AX|;ej%M+Gw3rcd;xIfmSQ(Sgq<YR)*b`Dh^sog|`{RCu7THPlYgOhhOg#)a3uh)oO3Xrxp3peLge@FuiCw5~V)xZy|uBWztNtt9tr2YiuR8r0n(FDXY8RE7xX#%sVg$#w9f*>m%n^C6nN^*TQ{0V;k}fL*Q@CnaY$ko^;as(a?!Z9J%o1X~;~<_AE_;2mi0P615j7WW_PW-8>>VDUXKS+S&Rgs*%n>X%ks2+~82f<4ao&DHL@IRR&$9HST`Bl@@vn5ktM>r5z8^Wz;2acC<s=qpPd!=Kjt7cDZR3bv=5>0+-G2z4v4tj)|1aZ<d%Q;*gS*n6h)TT(VBfo;^DsLFnN~WE(?UYxmOOh6eI*t_0t`qsz;8=VPEye(0X52upXVKlG#u&E(p+jC~gQT^5Vq8u?vZ*?6;-?NSvp%D#E8<JG&?Qnwqta9QwW)wzuiOGQ$D130G!$lX)yXef9)uaND=Z1gIg#yThCBwpTy9DF<RY`-0y*DWh+W4Tq>S-E5|GmL#h-aC4_V*82rjBJ*w$JJT~DY1-gYJ)loJW^%j*o}gnB5myUqaLYs`=&$0Q*wC#Ju}z1>6V&HBO#P9&)$nyl?k=%v0p$@?O%KMLNr2>o9u>44OZ7@uAo52NZ@5_5!qv66<B$k3Ag}|>5Hu+{?KFdWPDqDix;o3v9mCVpQT|f?7*}rS?y7Y22F1dCA>rf=V~PO;e#JCy0;@o`M6BVKp#$L_@vfoHQjmMg--~C%Bt>v*Rj`i&h94avl#Gx0!mC1r_Q0q>ick5n+R)Rx;*}6p}+~@W!Eg>p_W$={>t;`8|l@2gnkE^lDyaL@msW;=(+CU(8YqrC0k82R9{la(?E*mY)Oi*u=Y6;G+$q9H-`ohS%yr+uulyd_oV$}(Yh)HmVF=_f&~W@tX6<Iii(n8lCBPiy~qakgfm9i5(@M(3YXSqa-;HSysrVRCKuguuR*JuL&NPEOcKd|=kVC@71ix#ItBg{=D@$_>{sKL*)ugVhSaM69AeGCtc{n*`+bSfK;PTSv!D+A-`o7n;+4oPyq}50X{j%X>uw?AEHA~T!7r?!ICOQ8EO@3;+oM|Q;ZE$>LACj0tE7k*Lc!ZZ835=yb^j9WsKg`<1_KOLMM=aFs*NiBhA~k&>+!+xu<hdob-58Np$eO_N{?YY$s7SNA(4u)I~p1yCMK;b!|KIK?PxL^cCWq&8<CYxV>$Uw@rh5ys4Aq4FSwUj<Hp#pTroPe-zWWI?<JeeX!69xMpUy`tM{CY)n%WfpFjOnQ6J0qYvXdoTRRV?e3VN4WCXr<jZVCUiqAo|am1}6e|J<K0joni5Lr!phq70Vdco>3cqN#AX|K9kfB2_kD<WvL`L-5kvXh>tgUcG{IfL3(;)9cQZ^2I1cP>s9!$({s6g9?WMjH%=?^KOzkE6m}Ci(wy^o@3PPk)Th<}7(}Se=LEmFUC*>i74%nM2Dbr+L<7hJESbQgc?-N2ypZ713_<i+IL_gYxFLck%h3>4~mC@j8c0cUD+^w0J*2Ba@4N{_F9_Pk(#CR@<#qzx&${fBo)DH1O&4T>QTJ=fD5uc>KxAgwIs|-#)22zOH{6w{WK+;rU~qhMg_uKmGc{kKh0E^Beu;*SI+Js}%f;FO`C)*}odj=F_7}BWaxbI_5JnT2Ib9cfhK>&*j%xU44rUH5gUSpcT`&nRAcW(H|7N+rY+seQ9~6@9o~8;Fq0880T--(FnVk@Ooqu)6KMP{_4#}=c$Jc$E?OEz`2F&F85u`@g@%M$)Zxgi>gu5z;C$N!y`w3@q&*XN=`3!Y0X&tZC?p9ow_x)Ji(}b1G#+O1ewKAZ?p>;{n;wvFDsCJeX50ektpQkPHVe-ep;w|BVT#nDJ_kV-?X;09YhcK5us9!q0B_`BkL=WwZ{-)o5{X`PeLA_G;>TDfqaQBvaj5hdX1bsyJv4_6}Q;Zw)FDx#&eeu#K$%k7EI?2?obCM0ywd9kMe`bR%&qCMZjv)*mrhzrkz1{!&sI+?zrduw)5cr*i*M}Xz-tDaJ!Ijc8p1`bm`t<=z?(90N?$jLyO;Ymh42Wc%^Jd?>p6u0whm&(@7@DdUBRSl5_nmYxAoCDRHuuNjc`BGY@o2X|{(4?#gV|T%#Um2Pxb$@2p0b&DPA84X>Bisv;_+`u3sU)NI*`s5$k60cwL`@+|8wH)(VECyc(3^9^1<T7OQQ=+p-i^jae@S5=ClsRAT;<+`u^$i7<WaXSY@nz2R;FzGb9uS1xg0yzynTH#IO2C{=1hsv?Ofo5@ucP)GE>FbHdVfS1=CMqPOv+3}1aSfe^2e0AnvFIP`x*!>MeR%D*{?$07U8#*H<{L$BMxUsu^gVvGKs9DT%Wc*5Fjan)vCFL)yV!>Cj@rNX_#GlO)PhW&Rt~VsK=&GbX%-oTSZT|<@xP#YL+4L=B}Y3@`XJJpe6CqSyP~*ko@kfeJ=4hR`k!Ce*tcIF{dtR^D2=^#k&<FF8}&UG6MtoUTTec7%|~!qetyi1-RxU4_fHvmMuPLn5Pm~V)vW5NDfbP;#Kn$88w@PE4gKBoKBE(2BdvI^#o!2FDit;+<I0UWf<pnj#r97rNTkykY@hc<g65^$+WWk{Ue(%T2yy^?-opID7oDS~2Jj<7`TIGn#Mq;FxOeH*c>DOfB3}1<7TaR<bvMVoF!-xCr*iw>H=v_t@GWHRogXLJ=k6jnHn7zmeNQ(eX?%3^h3y#ksj%{Bbg`=25j4!Mcd~Wfp{+uN8wA(miyZ*}?3r>&;*_(~DElc4mj{q!DdEh`oYsp@xdFh`L72Kk48`!mEjd{jy&5VgV^sW{EyiR2iOStPdgmbDM$3mXaxkqEQkqh4a*_hE{-&H~$bp$S2M&$!E5@CTXMQ7sH+v2(+6u+^?vS8st4A%7yv2K$4YUnUvOKtT$8NQnx-G^pDDwH>>unh|YVj+}-&t?+9KTeNkL_=@!y)nE4Jr2aZ|rtDzqRtJIr7{+4wx2*c%BE)CXCZb`27Dq-+14DlM9y7*~>`d1vnaih`qlyKTKHjY=gIz3#$!A2ycYIb{KL>^iOp?5{rvc=*rbHeM`H<xp8FV%k1@?bAhF;K1MFhD58n~BC5=FFBzw28Z5vomcmByD}~)sx0CZn_Ehe~TtD=f+C<fHpH<4ET+Dv?(Yw^1tLPonU#HqC-B`(o3AR=?ZD=l1a{VPTjm)14F42m-*V641f3npLRU~^6J3yQ3iG!Sr*@eQ{5OAqK!FW?~stl{J8e*6v{$xT#(VBCwKkwO(POnx?GjgUqWi^dnm1onel6TWK+HBV_@Gv%I&R6mCVb8>vFowI4-7N|>2^TLdiJn9Gn}+w$#i4BdQ>y(getm`Tj7`DF(Pf`n(D}rV4d2oN!5&42s%hG*qgP?=)fk+en_otJDv;~B-jzAF3H_`mu~qs+85hzr$F6o&)g_rbB%vgKvoP%2g~N!{{?X$ri-B^s@g7{1n4e`E0vly6sT!y}P2b94VAFnFm;%6-u-a)2xpOC{qh<2!6B--NhTF_+R@n8Z@L|h%b2aiU7x6oiFw0bAB_|v#{<N{_`o=(`d(?Ui%#|qR6v+?ZSc5_r5<9qi9MspQ-A!VOmlNT3v%wI_&}(Q^bs~9VyDHHVC4v|JS9)HoBTt86{xvJ&-K$FDoe%Igp92R>ML$e-*e2eG_OJT~KIlvY$!Pk_z5Y<XZ8rYG8)M!ClQ!yIF%)&pddbOzBOd`h2{5Nd3=P=WX;3JD_v<mgJCv1Hqt#6-uNSLHb@5#uh&yd|NgxJT-nf^&QEbsr$jX)5F7_LTnDxz;q!gN9D=5$v&z9mKaj2RX`B~TQ3$^HQ2{4_RGw!RZlH|yvBO>+;H{AIJH0UZ%+3u`krxNG;csK?&BB0A)P}|UTz8tZ$skj-**{8`7FV>pJ7^ikTRlT!(og&nuS|S1Mm~C}Bu^f!jzK1E>y`!^Dvg~E$wf8+8mt49^4OUk2ONnw-BW~IL(zRo4nXY1lP!%Jv+~05oD($4oQaB|4ObBnQ!kTMCG)%Kvz|#L)q!D+^op038wB`*zZ6Z?(CKLXaqKoOoX<j+5IsuzE{;y{L)-|qI9BV9o#&NvnAu&T9NcKckvM70qAr*v0+niuJZ`0D}_@_RmYH@n8^v=bPj#9m|5{0D5%87HDR+9`1Kv~@gj>Kq7Gv?EF%S+vGz*z2*$_*4neuD|&HK+dr@$Em<Fk@NOE}G|hE0hYE4w8Encj1w(X<8#$>O6rYcBNf10j)tS2)zZ<U0HJA8imm;%p9XBk<2XkA&od)F83(%Xf!#+nJOa$So~>9R%`~PiA-(h`k5HL!v5m-7TkzvfUG|8Z6KHN(-tB;#8j`EIGmKpSdb0$oU6q2P3=r)ZgRp^f#&eYLo!L?jOQe(H<5DS_m2&Y_#_+Nv#6aU$h#!LyR=}cEqco;nMW!vsFk-PDs=BL_RZ^W)2Q!$k=E`06qEf<1A=A%?f#@FB5K|j9Mfd*z{N<HN|#&!mpA-2S8d@AnTv`VbN0LBzEXJ7`2{Os4~MB5YjnppeAWmtlor26R9naDkb;ZC`h=}<3y9~r@$`e3V@-#-_<g;z?)Xr?&$#5TpDg)vV!Rfe{PGXfzh&y+O*~H3jpvU$-1(=sLYKwh)ZXAn1dO(V9gRo4Idouh1#0nogjga<P|#4wU$FNR!d}_^+j5vS0Juy4s_Tj4ryVsm6c4GMgE~%@2Tuya8@IOisx~6rKYt3g*SOQb`Be$A3P}zrA15!1*j-LLUXc^0h7-HJ5wJ60%Mu@|NskAcXZjn(Qyj;FSSNe{h+wB=3B^OWgj6S$jjZh4`QSp?lrJhxEwitg&Fr=K<U}nhgulYanPA833F*=A0~Qq7_tx|#6BtWOv3>9shPizl^!awc41zv{7_{H|b%L$v(e%`xYb1scHYMgsw_0Fub2G3$`?xd0!;!HAh3w%ESDHk1nGRegsK}<J#RvjJio=&F72lRIftoLIx{5lIJr!kzi)#G9J`o4FDqI`map#egDZ0APeC?vBviZA;S7J79*hCT!2D0c^W0RqS(l!&oCGpp&G--9a5EZ1s^3PGrp`_T}Z`HCxQU`l{Os8378|6}|y|0RGkXrl<k?Ybv8OhqEJ5{br--%x%@{jUhq6TcDt~+Y^MF!H`T||r^68~Hs%I>oaM17HbRO5v|U7Tz<(;C?b$+x*J;mS!vT6asqK-v_OT{EVl)Hbn&V_|;es|D6-xkL>!)2@|zCw4n0q3UW@&p~cLP0Wa=kxS-ic7X!hzQ}|)m3^;dJ<56eXqcD!x))1>?u&+}xwkUK*yy&X_T=U@wA}Zo^CM2C0Fc^u!&Yh1G{|>wo~Aye@v7Sdn2%q90ApD=+&91h&``MAs++rBg@h!CmbPP1Y%hqv$F!h65NVLUvApH&aKL$8=<a^kbe`Y-u}!mKMe>G#-ZB3o({dDIH0b$qDaX~c-CKu}*e<n>lY87=TMgzhPypIp6sm=VZ>r+#_(DpBp2cGaYduD#GyV(G1Y9gEj?dtCG4!(5f81Vlc07)H8rQ$jvGT1(jGTR7o;Nxgog9Hoyo>h2K!|5-zgQu9w3PRLvnni-%}@e;oQzs(Rrs8CjCM@nJF^D}qM(jvhm)Sw2J}GgHn9#(b##RWj(i#IWhCl2$O<v8oJb)k#?V;Pd98Wi)gDJmvWS=>);0Rw%I-VM9oD+WzSkA>k6$?vTvQ75%jttA6&CLj^1=ErFq?UaD;NDoQnK~F4Nt{!g!V0F)IThQD+s*|;9MH&+P#vO5lcE>9^wt<?u77bFE>C1he*HgPXu7Orm>l-_^EVI4bg_ljgC~)%$k;3ioaA6{e6r`wd6)H2U_;jog}s6>j6<Xac3HUMV-XDo_1cgT1lRAhH=a1PC=#Orl7#y2)0{}V^ruw@pW8(jj1Vnh4{VP<Du;%WR01N>x~^VXPwZGea8Y=Wq>ZrTZ}Bm%5x5u7P_6#r4`F>Z@<RS$VAa#a)P#@9)N^R1s7#ZU{|PVBA4<^JTxgCjXzB0uQ1P<rJqLf`;us727h0_`X~ZkiDjjf?fa?~ps%MEN%%)FM`uhpCezWT9n%KnF&7GFjIrKLyYdvoZ*ekZ!xT!-FN3??{LfJEf(N_p00pfKgo5uVz1zC*uN7s$_D>7@^4W|q38-t5IXzEJuVbbr<Xx0{ACd%DkO_m(W>emMFv>I31M6ZyF!?8U(Ww958GRF-XsqGmilbb%5Y)~`$8m+liwBHLbzFp_L`G;b$aD!-Wdr{*aXD==vAX^m%dKI;KuvFjv(=6ZuWA(FsUlik)9jT;cIzcILT;@k*Ahx{M7rkZlPO%bjKX5}qZu70LA$xkMwm72g&bDfW$C3hf0bW*nq>~D2js9`G;#A`vRRLF&<W#Gv;gB8%<<Zv$IKq}_&Hj(+Hc#ohHtD$GR|CL`wq3%=Fs;n0bhjfnR@znF8&5z!h&CTZ1#;RB+@$JzUwF<BX|(K9n+-qzW0x{w_XW4ydOOqwSI}l3RlN4^GXNwD(qKBG&Ha?Z8e{g(ZuVGUajGZ*JIQB8namV^j#uEmk-hiKgj-Wb#`sEN+4an`Os?lI-5EOiD8Y>CQPj4udmrCY9J{P;!wjCD}8RV*%+>f%cSCJ`j4(^(C}@XuL<sy6=y##+cFzo&DgHz?fW18B|jNqxgrc>H*ddbDTdX4x_lPUdCeCxkc7s{){zma(UZP8$ZBm+^dauu=)w17!F5mF9iDtJ4I{7nOVjL^Kb;(Sv<u@pKh;oAkD`OIZ6rK3yMDk!P8d(w71yBy5OAA{b*I8$F{ctILn@`$nzF+e^Mo03Cy9%REQk$`)}<5Hhh(&xDx|`Ls+E(c8Gzg3dbpjH;7TbberFXSVFdG9<Sq+(Fi7c*TjA@M^$GSUJ-JQEC+FlFyZm*;;ilts{0icj<amTA($9$@d&+#Tz$O*zef!ujwt*kwn*{;d=qRUw#hPB~EAQUrMl<Dhrhm*c8=|)~LeCt!?wM2czglm2l;^6M9jb%fW(=h8zHs5y@zt8rPZZvKrLupgi(qpSV^S7g75*E^e$se;Ew1yM?_H<W8a%v+|703AsRMb@vME|Gbmv3up@>ZH(i<M?YuP~@7nt37)VcOTn_Z{ja6AYtYbq>lw!jSV9BVPL%daomnusS#!RcdPw+{Wsu`LGCIk=0Zf3j5UZQ@UCK$H*ZZiZq=!fODa`Q^(RbR=r{LcV{)W~a?ObI0Xfh~|s-@UFw?HRK=oeQ~)n|2Z1DUmRvncHA-YB^8g_N@jW=o2FD71Q3)LSi5*Du^j??G1f2(u=PR2C>=#BM|RNuFKOC+!h&AGHuFJrFI>?@5C`KbmHybKZg?}h$%H>Xj_DhJ4C^-R8y+PQ8(oMk?ytfBTf_W*%<Nz>$dH!dQCDVsh)4{;G><&%O5#QXm$z)KiFaC5LgJ;h*7?2cGGjN7ZZxbSa=7hY`0eAA?crEf`Fxg+nAyVAVw`)O0Tdc?gUQ}Wb_)0hB5St_0m5Di$QxD9dEI+OYcAwVP3mYOX+m>FT;^sfDNmjjovBzgMEIb=*!J6*Frv3NIfaz#gpUft@MLeJ@CxP0V7PMkpjXArJ=`mfS8^1vBBPDmop_1IC0e}CmsQ$2%oZ)!V(yo(Y|J-MKCTxCIpL`1yH-YwTNU>fH!jVRTGpNTMngtV_ga93Xa`=K$+bF2DwU~WvR9+(jU1Q82X2L6f7kP*SbOERpCOrYkZ2_uRyNBFza38cP-t5j`nD8k5Ro6u8Z-OWYFHQ^{9%ViflZc)9RI_AEQloH!vp~2z=)-hDAMzL*O%eK{`~F5F$j34NXuOf5<!1EXZK^`;9W@s?4Xi!%j20R50oIFSK#YqQJMfJjG;+op9)N6y^1I-6LxDw*GK!sD%J3t(O!lXF}m!yXK>gk<CrAhad^mS?;X2)!$ZY(R4=0txmW9&&*DQ_X45Vj=FGDKU+I)8uS7u>T6T%Zi7AEYVZ&5)O_Y%FIw*uKLph>n&8IvD2$nyBEFvR;tV8vv=e#HzlXt&B<-yrRh~m?YxlW)!P$ggMc553h8hi5G7{Q+qZ{g$8iCV~4da*&`36{(WfaTf&1~I!iw8<q8>i;B*4(T)YI46uBWV%OjLR+Q|mblblnppnEF)H5X<6fhfVnb^0&*kLWKX5RJ6oCv;LV!22qh3`=A+jU6bt0A_S~^p$TC-eEch%_#H9RU^csA6Vp_Chl@GxmwH0=P5sZP7W<R3^Mv@sV!9C{%A>3D*gaLt83;6C8Ys;GvHH2{Md-NYwL#nJLxfojg$Sh>thGMh5EvDxTjqp=ZH1s}!WG&PKIMG#Cjo0S&`%RgW_W6soXFW|}Mvuu+~@TOL1Xu-<Oom+gDJ)9RNUB#-TX-0ubN_tCy87-U*-jVh*B?$u}97WsnP(_%czLB(;0h5lb6JVhJ>8O^mD$o@0oNu2~V?xaadUAPIn6=Up9es1e)LU_k?fFZjmQBWZ#)qw|WfD^a+*ic?azdKXk`RL}R0Newj3O&o0Tm}69a7|eufio?)?9s33&oLZMnT}L7{Ve~UCSAeV8rT)KITE>2)RJTO(R=u82|MUO4<YU!($P@W822mu%2us<7br1SJ;|Dk-_iiZiWO*<jCbYwyA4AGd>y;HAZRJw(CPmXJTkasy7WHL5-Fze@HeB#l4PSEH`ff6te}~9NxrW)?yMFk6`(<LNQ3fT&+rB-tfV<;(&wM7fMy&d{#kW`_hK%MA_hDg=g(Mm?srZol`cQ5C%w&S1@$J8`OC80H_P-mFXUFueQuQ3T_CA_>ebIKFFaiIiQ$L#1|ce>P3Q$jS}iQW3j8{>|PJE)ev(Pz@kFl&^EL-YsOa9MMn#jvR-`89<}v&9aJ^=cy;NlX@!uZ0Q!h*f@grTgzt;5n0u3Lz1EsG4*Y@)TWW4T3c~TYc%ChDxz{;!<J-i?gbK=^z?a2Vv|8j~OQBk48y7r!24RaTzqPfX`_$|$T=*r+g*0ze?cHqc6@Q-ol;xxsHJLTs6CQp*Y9R>^gjS{hA(hwGJg1QPX4%w$*;Z|NJn2D=cIl>-S{18Ppt-Qj9cIlar9kaW$(9{ZZe(<oTBJflU(51tT~E1XIsFkmVx*MEw5jzycMt8P^iqAik3+8|#>57c#D&d?I5X@ZLe{e3A~lA@T-zTWw4pVk*s@?hAGxC&lXJTlVTMKe`9lm)7;Ets_A2UJOU;id>s&)I+RGh+N2_U14w9^ihC17zLF#nwVoSBY`?hd@A}iEdWwolO*Dy)u&0Ewu;X&6=baopzdp*qzS^BHF;jc2{qf9b9fnb$FLfuCr3BySg<;f)Kljah7!FCx%PoiVdGk|Zf;;HTXpyAslGk=AvbC0OPnRVU#iFi$34p=)$<d@dWk4SNxGz8H&^-+(6P{tm1P%3+~dbAbJE*#ceg=Lra;4kInNM%v^_CwOkIwusMv9{OQ%QQW|F?bQN!W%~%^CZMV@#<|caBPEJa;2#b#rUecc(@$B5%1ZKyy_rDc2P!D+0D4uv7M<QyPi|fe^?Ki+;PTb%@Bs(k~IBJelwfPoqcuKbHb+04AO6;`#_x(kLQlb{*clGib>n@q6+dc;$Fb5^J-EhNyT+y_s<ysW7vxqYgrg*W8vRmJ-+L6W(pI7iH_THM>X^9@q->7eS$$%!t^SaMOUORESo-a)ph(Rw{b-!X#iIiF?US*L#mm26<HD}Gu<95h1mqjVO4Ajr^tz_O@p0v^XMmzq#Vh+gjC40xAZSB<EDGlRIOWWAM*ljdsKV~N7ToT`z;x@6pd<L_<c<u>WWVEw9=+-XB5a%`ce*7WYo)?g&6OhyrUG$jjPO?r0kGe)pM^k)Xwg~zCr7hISq$S&k|vB&QxaQppOGm4Jc)P*|UPvuoopq3<NMA0vE`4nRISnPQee44Ni_S?*&(7lKjSBFAs}30mp9^W#NPN-;NnLqzZF7TjM*B!l_OtEF1T^=9t`M9gpu`fR3FpqBbe#zT<r3(QI17UJ^zLup2#U%jY8Dd*+N&hM9)H6I`KGB3d18^R#J|T0NGLVG-ku99?+?@>Nx&&7nduzg!iE#_~?!qzPX?N^c;9?^GXPQHvL#*}(d|#y&}>k(Xcg4C@=95)fK6R(@p9)#vFEZ##%NH+7yk#$n0S@vO481d<l@%*AL|<X&M943>P63Y$HvJ-o)*0{gFcw~v{z6yz%!bs9<h<!z-bQ+ABTNi!xOK*n+)w2birH2Fm3f>-4zn394?S0Tn7>#TBRgH}&r8$_8Sr|VN`pzG0CJHAWR>UQvJw!Q8v6e{bOt#0JJ{T+-hIC)U};X!f=7m>F0ASxM=5DLaw>A(tCQr1c69k-K@lWde_tf9`X9&D>bOgRrJD2H80n+H}lEsBf15`=dXbjRAi=TqmthAZ;$ULz&%e^<xghZ;j+V8Qg0LEpD!(4|AHiK_=%@ix6COV{CEtQU)j-JYtNu+kq~V)fRviAYs$@j(+F0g(n8mcfN}Y73QUq>tv?FvbtLuGt$HV>}~NU1XMAE`g7xK`*(+#Q&Gz71xHc9~_?3oHXQ|KD5cn0vUS{Q~c5~xEpYu<`jZe$I6P1VD$plakImTl4~{t2Ic9Nu&4@@vFnQcT*3L!xfx|IAxMxN)8Yl^>s(zMuW%*60O2v@_#LfS^TLdkgodKbYfR;8QaN8lkNTFhIi$gQb$6ht7W*u&l!Svu3*qG<yonzHesO6l-mO_+;0jyIa%Z%@jpN>G9_N#kXXfH7z8=^GNhRinf7TXRYw_JQy;BsYB1BCMZFg8M(3XO9>)y&388le|THU&hN&*q`2n0{(67(fq)fgk>LG8M!ui?Pje}83^=~z>OIYVm9ZN`jw(0I?y`>#xmsasVaYE5vnxs!q17&L+tH2y7&k_Aqmm<*@rPM-)-0mJbWq=r;<Hk-!EU7r9jqKl`b-=~N|f4!ILwNajW%Pp$hXL971q(}2&`Qd~ouBTHtz+U0haMV;vh!U}v)!c^XFvuj7M#d1mtT(<~m7o9g=TBA(g7p<&%90|<Bi`stvzpihb{6x<*7#zM;lZqJ>Mn05Hp2CuOHVpsH>H!v=&o2sk;1MfdEa&H3MpNyi%bQyOJ7qaq?B?xCO`B{ipN0+^pI^D{l;{1=m%A_Bg39l;Cptlczu_XbG>#7iM#x=d?B!>%&EWkPSz>fh^^9&X_fkB(2Sd{1@Um@azSU=4z`!5Vu=L2Xv}zB*Shs+dbf`|Y&vnHFl`C=P9r-zdwcZ>E4U5vDcGm!$!<W%{!mBgQ1q6rFeTLKd+OfS+!ZLyS7tD8r3OlRd@vP7I;!U!xS|8pO#S0|jj<(xh)EmznH9)|W4MM>-S&VVM?GSYR6@-#=A<psmv8B#TE3xV=2?a1k)n?`>7Cxj=Ed_hVtN8vX6F^8!2{jmzc5^xlj3`3!oyb7v0Bx8{$Y2eii4I?;cW)-$=Gt)Qy~o6;n({FHTl1Bwc498y1C->p+SJ@Maz*W^?82_0VFMxW|Cdi)3;e;E2$-Aujfu#-Thv<HUnhdO_$V=tdE>ul}v)uUJLj2jBUs_41vEjXDU<Hc+yGhM?)tvapY>DV<0mr+p{zY9{j)FO4MGUkQK)eck_tgq&ymOYiH}1s75*irA=h9aDzh?k1uUCq)^l;R2g)Y*0}riR$AySL=5$gmv%fvmr<9z+0hPdkFJ@!_iygE%T1%G>(N6NxNLs!y(jB%Or&Ifv&1wJhm@qml%1R9l66}4?AiGULJvnG+ZftfyO$0(G?0gLCHU?gU0%LB9|MK*L-$NYSh`F7p(j;nCfCMg?6b)4vRM4q$nWCH#+$Wlm#Uai_RV`8uimwmy4~P~%YrYf&TV{HDw6sez&SNQ?w(>tL&4j5g={xwqgU}X);Sp`@$xR@;M<93`|aqwZdq9y%dNuB$|ZxDVeA|7-qF()+fTe_WV2K~uGTt8iDhh48`M$Ykt!R<ZWQbkX=Aq^^+>JTHyt9LlFI|=nYqSIx71u33892}_FlZIOsHj#{Q`<=|Ju73q7jnZWH(f5u)02T1qC`r0xw&O$Q~1`z{=xHzy*LzUu+%mhbEgR;oI6<ym*C;orOvKEDdX62c|{IYL7}ZXnK1n;UyaQ>kmKv>zCXd`|!aJ8Qt5FqkLQ@WuOnIGkj8Ow3_Zb@4_bpLS<F=zw6lRI%jti^;ryfKLI7CiBsoLWA%MFtWAWqFkK%1vQXfJ@Um-`@KDPu2!G}I^NsXsK0?2POiAAB_V_K@P4ry%aOh$|<C3i=8mccT<Y^#9bG9VKS6KTT37W63wVOkOh%7@UV%Vn!jeFAmv1nbD0?R&-jgqVb3RWw?97RP*FiBU3!(L<qd%_tbYzYN=8HG!0Gr3WDG~U;MR+Ecvx!0i8&7tA;3?_+G#XCGUd_{G;nNETKggNl<Is4W4W%f*sj3Kq^KZjWJFKgo^@_t_;G|>09@+_zW|Mxb3vv?(P3-4zlaa!t2;<{VNILk}1Y48gxC=Oj6BnzIY)b^;Bdbkric2I3T*)l2OnNaZdPzC_HPTjvmJ1Q|rgTVkpRZ$XggleNozhO*N&U$<>JZ$@TL0xVHOQ^!8tkPo`PclaUOh}|+?2d+ph>1z-%CLH|QahT=hTW?#!bW7J(^yWvQ+(o+F{%nF;|uO3*0?eDD_4w8?e|H)*n7z)Gnzbcu@Tkm)#^PbV|Cf*=;u#ARn*5?yYAw0#alZMrhJr2{bU5bca2WGg^JHXwsFL*B7b*O9s#REJP=t;e221Eje5cAF?c1Ierd0|T7USbV=E$PwE4CcXR?!?r-REH=Q)GgR^o$`b#K8=)^{#W6~jkdBosBqWkwqehwoI4YmcMCT_*YearBLLbx(hc&*m(7aaf&)<(25f0_ykoyO~4FC#QMVWQKj|;Zk!})kmpVFBQ>l^NYQM^5(a9@%eB5@eg{Y>(9K-BGbJU)*mh3575fw;-CL|{PEM@UeMKcGu7|@_QPMl`w|a)Iz5-aum1V(e>on1vU1@wng6#>st&O0U&c+`X-Rng*r#D<%lS{g{_x}X|NQ($fB7{o5B(|y1LI4r;A!@+hO_zfsMAPV=e~~ljE&Zl^UfWxYVdRUHCA8WYD@J;m2+stG;ZeHB&)Os1@AWSabI6rUh8|iHz*ip=Ml#F+jTU;Febbn*~WA;ZJWP(v(b6_VZ$@4F$(Z*A;Zgk7jwLe!+WyG6!4;IoHQ^TF81)q(_g&cV~3Q}i(XnY7Ju8<!c3=bjW16?s^3B`pEp5gar7JQQbvEaN&w6XWnZ6ap<*OTIl0%`E}x&4>fXp%-uFsNBjh)&E^P<VgMLJ)l%ps!nf%E73WV)3MA+uCZ{U=W$0yA!Q$`?PqKoV+x5Zu~E6?uP+gZ&mHnlC?e7y18WfbwTk%a}+d4oIDL5YA)tlXpgU^12(oOThi+O+naot<fKklj$0rH?!AdB5#ExIgyP?Hd~WXByltG@Kn{k}GApcNn@L+%>>=Kk3opcbz3eQ7c|48`Aq;HKPE@Q{HrvNiv_D<&flEKg-(udO%8@Y-Li8edx>u-O`%v;exv|n>E|0$J#*>_sl)3(Py(Yvt`Tc<+ZA)3aP?<=r}c7wjydy9btgnVAwp%`pZq)Uj7NAF9dyq*N^6(6E8aTfdswQ2+UQLqG+oC30}GGYe%xL7JA&y0g+~`(E?05t?ug(rl~>Bf{#{s)3|}`pvEC{tZ$%MT;g5JUW592;&IqL-;aq7$>?o5yj)yM=i$L?xO*%*$htmA#$6v?yRCpV4ry0x<H`9(k(<#eYASw@A1zRgS<rG@^*v0rUuEoaYsN0NCA_2e?>&BpN)5Fjlc|*h>@v{3Mqipm1|e74@^1VusNT@|lV0i34wOEKv?iZxme8&!E}JLXrF+jb^1A-#7e4mw*GGTeA}C5@uU*8X*v>|M&&9-F8Q<2E&usG%T$Z07Gix{d*32DLhOUv|eKLgKP*pXndTP>r12J*2Bhd&0i*7@Q_q@~SgxE+c-fJ>A0+>pTjmfxjV~*faz<#m)QwkF4GzQz}eUYSj>9+PhZ?9Li_85X30H3!o|L{fUsHp+`h*1814l6PCC?4)zdNtlY{;r7E{hr0P7=7K%aW4%1>dmSA{`U>&s2zL@S$pTlN%pzB2#yVmwMXC64M`dw-F#s?#(gTRJQ{th>V^ajyX&2dop)%gP~ir__xNH5z(0GoT#`8D>@>=L3d`jIBw30$b33Q?qEl`GF!d0oJ`qDXyzom-7Dlgz3d$H2KWB^a*ngsOH;>*q2)NPop^O|%^MsV9)SH~7K&-zh=NWQfCeDFFBm9bSXXBaQh~UkxLyN{jF}^z_=-TR0OC)dc-en7I!<8%#Zr!n4&8BXP@e7K4KKOcDMvYqh%JO&C+dRiFRpev)TkUX2e0W2Qz5N@zq0Vp3ylRd-_m2an1tOm30kjF@bP_)Qzt1<`_mz%WJ9`;PynsgI53%>x=7$Mqo^9|_K2RKs>PQ&iuN?-QlKfLmkHq1&Wvt54GJQk4M7VKW<jL&yoO2<itujU~%P60T|03$kbsw1t6-)QGxT?HKIk!~n<gAfB^*S-b551)}v2@&FmEI_quwQ=kE*0l0W(UpJskTTrR`FqisFlqcnhTWNeu+XOv!;SUv?A)Y)cVAlY;{2uDPBYj(B69D9Ooi+p<FhES?W(P-c+0_!y>E(7AEOFnGaEn=G^Gdd-kK#qg9iOoM}(FOruxj*)yw@-L#7~+cXTki%oI!Rn&agGaV*m;cjGei!x0@!#yLSn}*-e#gT0NQ>ynaetm`HjIF@P#buxR&-uKMZQjzNz#fH$s#V&nk5^&n)fk+ek6*@nDvaxS-IaN@3HPk0u2tfcXIe<a96Q-nb(Uo2kam*%&BCy6#|IIq`_H_?B2&n@#d|PMVpf)I1#FDDq+y_9G<_?Fe@(k_VF8eC2CI42kSBL?`d21TKB27PT)3^vW<^|&_P*IJ-b{@=%0<kMbjvdRSjhti3qNgQy1psU)E-qG0~;kuGeyD!xYeMfg%l3%6bF^GX(yAI*5#D9-3%{80`wXXRb5Bk*qBPRKZ$^a|COHW>d3uem~+j_b@!^Kc<00U&F8=YQ+W?l9JYk_q5SJ!fe$+WK-!r;bFV*?Z=3Vld2Lvjc9yv;xmJ~}Z3ya`@{(f-#XJIP65vgZ5E?MC(}++2?bjZ;?+#@>)o5wc%H+jLQr&u&2jWhfT>{vKR^F(W{ZDLRP{_iSqb_z8hgkK^7NiuDV8bWS4$l_iAYrIl6#2Q<?#s03V+pXFnJMn8oRS2{qazgdOf}s31@z}CL)q@EW2f%sdv!P_H6oPDU{Bk$b-o<2f2p_^$-Sq^125K^#|o#WJ5_bFe4Qf5qsk!x>zHSC`mG#{LcWI~+a02_O|tA)<u&m=9haQAN}W|!;7iGHRl9B3<kGcVZ5gX#gisY9u(;oF{wXb^%EC9K{Y?69E5Dj+L$pP+8okp0Tciqii<@uMwzTF3KW!pY?<G_HmTHSB!`syHX1U4)jNSOZnq6Agm|bzKvDg{M@tTLkek=o7o~S|=B~CG<f|_U>5KQN7TIwAC)JIb-<}Q}nx#-bRqjy%KkPTTmaZbu=(p~`~tJ}Si;B0Bee1dLysT(dA%e_#!O`^zeFd@9=?SCLn{f8Q0j7NU2MXt9(setKVxL0u(9@(0dHIkmr6G-Ax+Qkx36vR@{TX5Qy?FOz<7|p`WF`5#o%YqToh|}eAk5Z0CD^r}QGD3jGpQdERW>C7v)LO2eiP0<UFMe;qjR*$F;uGHnvKT*YA)-S}^{R=(NtuiVIY7_3N=)Cd<9#>%6umYNkFAl1WRj#9&q-8oBIUsE9~(OGNjAJ^IXg*^cS(YGX|q(@@Rl{Qf<k;*CCroD+Y#}(_Za);^|xu%cfUyDc7KY=ey7PmGk|t~QsfXd?+dPIGI-!(q)VYoE`ZA$ew(YdaEHt(MU6T8U2<3{eCPavm9T)rRE?FmW2-%DgcwSTUn7F8V`oUgMPYBk_O}JZ^W0qeLCmox!d(2m-dT5iDBox7@z+n5%sDY$i$H$)2kPH49q=X|r|QP@#~tqc(_5j-VsL72@FN07TfvUTBi<Z3Fu4M?_&q`_5hW*R8ssn7`w3OA?C@>5$Ql6LrAO8E#PQRPniq<PRL?<OCCh^+h2f1`+j~_T$?cy%1#4^EY2favgja<GhjfmUmqqL@r{%85iBn^V-QEZo7qBgf57nf{gUvAgjoc}Y<JT>H9<xyW6Twai5{id#si;mW8~NC|&%s64_Iy!kYMFh_Y-X>;BqwT7A@dbp%>+AMPe_k=AF!avySJt{nZQ_LiY<b-FwE`apqIA;W)Sot#Gn24t`lrUkEW;gTq7}ruqiP}y4BKxo11~X*~gs`9*&G1C}a;0xZDV8$aLT`K}9w#4Mh+bQXIY*J1#plby%c~Vw{f{QAe_;qO5RHjUU)2;s95LYhyg_Jd!3wSNEB(T@+O|e^>EJ%;pT6NaDdj7X4~$GIUVbX41DL{u-4gt&SF=f;3qEIchnS65IQ&T6Re4U`LPXG>dGbTq?EGRk00HL!TjXU0Ng~S-bS2%Jt|w@oPl>Q65axWKGm{M{T{xB$_*jh!I5MpQ}UJeU^c!FOrXHyzr-slMQEDBO4*%Hn$#JIcZ4cZYdZ@n_{wS##EHr3bybk%#VDvz*=pUs3~UJnNsh>Zg(V9UCrt_$PK888Syl7$sEm2Phip)nGmP4x0S3%Id32B@lx;hVrkHQ(eN$zR;Cym-4@lJ+`NXC*B*6u#K{x@Qu}V$DovUu_zup~)Q2=)b(;Y5@hcEuEc1r@1~>p33RhcobJweokOa}vb_|N`1@ZTo7SsnK4bnH3x4az=IIjyG-0zz1^4mYQX*R4#-Vo3`mS1E}jzWwEJzp;6xSF<m>rfKgrPgtBkK1dj!8`^EK)X{ywXpC_Rh%7PNU6}Xc<f-U$EbA1e?gjni-pDU8T>AWUe<by+l$VQ$5Bt?x)wUdz14`3vk%PkM%SW~Ban%A(Owt`@r>;kD@2c$^4@Pqg+;O%N}!LEQQNEvpVR)(js<*Y_5eW?)bZ?a(zDut9?0D$)}g76uF$}dBcr{HL>&iNA;y&xDFnqB8f!YQH4mKG<48#s5mUsvM!#FxeP_ADT4&hzx`O`kD<^`BN`ZbkebAD^;$1>MSRV#v!!B{<qW?%rw%)g?sW^_%zQv6ChlOwjp_c)iOG90|SMoAqN$1N$yrJBk5Pt3D2B_c=>G%DK04&!uHd7Tpl@6*Q+Az7%dup0l(^5<EmrA0)j|Hig+z94C%b2>8q;`BgAPOh$Oari}lUUc&&dXLS$y3fSZu#6Ps8rk(6xbWVcFS>$3Y{pvj_a>6HDzxQzh8Siw0(rEF>`Ufv18_}+xfBYSOBXG&}Dgxk;Pbf&cV_`w-dUwV)^au*BBa^C>l&o&^FWqkg%!XqKpab3N=mSQl5#2CZ(hChspdE<~g(U(@1__60OYO@9S3|MZhbutdz2SUp4;o_0%E>{|L6|j0wkNIvTWN+JHRfLg9=t*1Ksho`U!-PNr;_Lh1QsaJQTP846zTV7DEhpp}78@ExUhTmSvFq72ynX<=VJn-L}fbxks-=c(!S$JB(pi&F1HlHdw5VG!DE%DWFnd4~F4T?_~&|Ku(j_5VAgZ=w^8HGEugl*<-^+WF`>uCRFVfN`mgi*S_42u%i=F2Sm7;9n*#r%fhS*I#3~HB1<&#jS9*+Hv7kjRHJXM5|kxz4FLzy`)CSt+nJ@LP?HD*Zh1kh0B&vSj>Jjqr)U<H<#H6v!=a}!)m)Mz0~Hf@@r4C%pvuF9M+5WZ9Ysk>u3%-VO)w9U|fSaUbFL<*`ppmN6S{bYuncFjTK48nM-Wnq1M_QdgJ)rLpa>(<#v<z^xhZ_+J)cLR^{pUs#`8g%nuY7-{jA0X5=Kw5>FJ&>j1Zu=2cLtEMbRM79ha6*CWk*k%j%%TH#W{y5xF<gkY1rvspj4F6`0EaD7x?9M^iaTtD)m`=Ezm`g{4@#^Yd{Tk!~mIF26ysP>969)noUwTf*}Gs^ECyGcrGJE)OD&@yp@_hAEnc?&@0`yc+LU=4Sm5$No30dcjKwH3;FGVQ)KFR}w5S@rt3>1wi5%5yUzSj;3?g>I@lr#{z<p<2oE+UiJ)hlN}Hq72N(6D$wqv&k}mS#ZeqJ@3G5Pf{xL{&AFMiEZXpW+qZHKf6M%0fG|%VNWqPJW<-dRC2pr{-fyVwPt^TXf*Y6EE>mIdgL62&|#rRyRz;t*gbwdidcqXtQ^gFVZc*O>iy%C3GbIniZTWtUbPs@a5A*G>ArY{KCXXT{q7*fheqfp(@5X|G?0x19FTAN(!cJ*GI#;cs|J-m0cICcUy7}P%?5biwiLHQFzEy9V5`18wY%JBA~~l{^||;nFRb)n7N6KWVR2Qs2Tf{~B^R9uu!#ecgsfHu<5mP>I2K9&;)lyT#25W*|85ApD}5R%P#k6N)C{HpFEt8nZKw*a=nq}H2@Nw~?Yu%OP8d**F$GL=V*kc%OIi^{8I<huj=XF3_={k}fcgS}+`!tikpm$Mp##2Juxb)G%Ndqwm?$S!y;d@0*~GGw9$P2l_@h;ADSB`@&yu?Y$FckB5&<G>#n^JqhNeq>02Gm*24l$J-dLTDpk!2O9vGD{6jqmK+{TC>sc)WM)DkRELb@5=XnM_%0n}I>0~qvsG*HqG{AANAJ0dZ(*hH1p(I9TIXY!UP{9IhW!_s^AYDTOXX&*(qv7GvQNqBY~TaI5D(D*oH+sBounp-BakBJt4lfh-3Iab;%TGWt2<UzfhPYYNqmDYHJA^PHvjd&FVnG}>)h>ToEzQf~!VB8C6__FcBeWTex2V?P(6UM$9^&NVUtjNWVa<aUV{al3acHgpE+O5De^1`Cp6Pc}zU^c%odEDi4zB?{!3;;Y`eocc+N#@@s{}<Ga>t!%-Tx->#0`=pa*XNsfaymQpBRkXNW9qCy#aneO5G5hA7~R7~rmz~hoEv>`R13f37;)%^rld*Yl(1#e;B4622F=Y}jshMl$ZdWt7!K@H4j5(Rn}{ea@o5J9bS6oFqeQMe=?$=|EsIqf=eL*SF1o;m^zjlsc&La76u;{Xo_Eppmp8a{;^ahGq^8S?PJ`x7lF-n%zDouFMAa#>f6|c9w{s;(^!JbU6v~Fju37Ev|BleanSE3}?fDnMSU<S{e80f2Vbu^lT~rn0Sb`9RjkSbcO_(BD99#ew1wf;j7<ZkHTi)5deU`g9aA0E5n9<@r2%;CUW7S7(EeRG_7r<r2h`i#F2nLMI@^-o2(ex-2mRDTUnZrDLMTx+1+Q3XUn~TxlTC6M?A+^4RU`TRUvMu(`87#ZPsh3eG>8f?jXYs)k<2(#!p3@W6Z@jV{yrM=7C_I&q&h<AG{(%kNN=HV=lgq%Ew2`o7Yx3OeO?eCuEUN*~f3%jnhP>-Jj~;P)1yV{)Y-nO)ryFzKNe=aG`C7MYpJKsSWI$$yo{*5j$E6dskVW%iuR#J2h(+sTk@61f4cGS+rB+HN4Rdm2oQ|laP8f3Pgtq(<7-D#i!NVOGj|_`g6r<uT1mN{tDK@0G(KNtz&iwrY2ZKnh7fwkJ;3M5}UM>RQ!T{jV3v>O{BcG{Oy;?4(yXtg|h$b{%>9*kB45i#a5t!liG;XGhsm`LG$Jc;m3_B0Xmu;a-hv?8^l|1YR&XC7PDS#|$YJkCvZerY70$xsyNmOO6bd8*%MJPbU;$*K<F&TIwQyoc-@lm(|p(8RVf?%@jsBG=Ho(antbEdviKUR6lY*RBO$n&i(7Q1ey+$R}WN;WH^mBCILbX7^ythS#T)+_{Ov~V_fN7@=RRiiD^`YQpOjrzuFcLq#4g27q+K3VK)8LI+K0nhmay&4m0%K7E;tT1ckIC%7Z22-2DF}CL~5edr`u#^v5SIfjQdBJLQG$(_QX0#-Hngn>NRuYG!u>v+1kYlST7G}rp*H;63E=DUBK?(xb4qHdZP^GTr)Ve3f96VZr2Mr|T0{S@e9HysI$!H%zT1VFKfivyJCrB#Sq#I+(B(g0!s6)}<R&qlEWFLW_hwYD=&y0_TL<&wCw(a_m(&QI9d+JStNKm8u$sdwULve2g>6Ew)qXmaPaC3OHrBMx-#$pl~k3ez1({D<`T&+qWQg2NwM>v>$olphNXBCtf&Q+Zos`Gd-_)>`On}H`4PMuTQ*wdayHzw88waTj*S}msBL%mmX&V*YaBsi*To18t!p)NU~dO^e&9faz|>D2VS&FYNBu1>6m43|s2yH)`#D&!4&DyOAiN)V8RQ~?+l-?K+;JzfV@4L)97t}n4q$WZ`&A{wfy>ICQ<+x;0G50RM^XX-Xo1Ir%;;dop;&z8B|>zujqZL(r@Q{l@^(*n|4cdQlSg2&DxD6jInM5i{K<Aq<cT#k-{rB=r;1eAj*%SkV6+L8qs=o&JYvp6)eQ>~iL%WEBUlU6i2aS<vaZh4LDz-wtOZEOJN_{<rxIt7{w%iLksj8Y2J&XjD~0p&)U2WIA>&>PnkqDeJ~-@KMRTD}HkQ+u@B)jd~C{3QoHoTT*GxaZq3v*xCAPNK;n;4ttn{yoJ`7b1%@dn{tE?GFzew2dgX;TO^!xuYBFIJ&e6Gi=3{Kg0lqu@-M8I{}t^>iSDr=NgL9UhWV)s=o1Hx6-hhH0VK{ZO|ZfI(M<<_qY4DaDRg6>{P3)hJt>PfXQgqNltm&4`HCV#AU#zf=SQ6f6X4c?P=mvA{%^^NrvZ}9HH;ShuSYwz(<};qCROZp_l7XIjbtpb<KRP8Zx7MS#clKZ-~7s6t2#;O>QfbaVSQ-CNBpZI7_vn9O#go<i!p4FtVg)2B<vEeoqke6e4)Xw`jQv%P!p`U&_mo%A)e^hr$$zv?HEtWLiV06K#VR5i7iL#MoVm-juj{TMV44o-4ZI5)C`)V-{YOL%21j)@h68w)JHbCTL&3U3NVNRHq@aKvHVRj_3S;8V{P>amHoM5Qg42%6)skna$<SzB=qVVbf*?={M4SpiYX%Gx^3gv=c<>0mY<kc~J%V7;!J))_FCllBD7~shSsWQq>kP#s=b)>0qFZg@1$f_^!{HDNGC|I&LyQ!VcP$LUkYX@aPi^suHGGxh%S7e_`45nX9hjN4bqFDoF#lvWU53(x2&SSVNm-m(JDZTFGHmYzn8yiK<P5optl*Cyt~XQQ-zTSnE(fU;3AqanrqNs@AQxk9mQ%Jt{tgL+j&Xqth}OwVW8(KX)>BiEt;YoqW=r$MoEyK$g;%a<C$!Ugj)7Pbof1xu@D9^Cl@f<W9$0bO=4RJx?l^eS_91a~cjd6|4{@=S*c*4*EDC)qqmwmpv;u4SP{?#6SS^A#fr7nZ*Hl3e-M4HaIz|v2YIlpyW6HdU;sP2{>Y|Z3Ia55p@4{%)lX47<6j(-hmWOHRv`z?sLsCxk*|xJiVhgz=&pzlU(N;k7m>E{xlXw39uVIYRl&$;d|zcQ-+y_zmwA}0B`o$aGR%1tJLbTj0}qyXXIX2qKS<<4i$>|{SHyEyc0NS!q<<|8wlY$Bo<iI;st0nus*ND?a$%8lP6`*u)YB*0ii`><wss}^&!L@Yvm)yI4qeuo>kVCK+>X~xftz=+$-#X!ICdhVd(49SFa4ZZS1h(dE~@7VnBLxQtjJ5#w#(@w#!CR*g1dzGL{3OWsDb~$tNloyedb*loU+53Nh|jXO$}(w0hj56@taI!%wS^cZWjB9mzZ0^BgR@p&g+TmZKXvZ+{1)3r-#h5S}-k;p7x9B5mtIR5BtV6pXXdffcT#*Sy!!8Vd4XOt7(kVL8;<)kCO&*HPJMZZwxR53Foj6c>9XSnZt{7g-|Tbna{FVfbDnCGUS%$KZz=Lt$XS^pio~w`I_!L#&CbCsrFlqJ%ykrR#9BmtiO(lCPfKN@g&)#OkeS6OpRi;)5nU0wN7GEQ1T{)D|kyNFU9&VT>PgUH(a|<4oShp=yg+!tH!Nng+e(8WaCtf>&G{%6@QoP7~5l;s+rX9&K{6Ko+@=Y;2Gxv7=X53mwN4f>p=LijI)xZ*|=4aH8az&4599x+N^C0%h#FVn0`KK6GwI*-Ho#WXH64!TCB@*TySc2{4?-#gt5py-|Hv%Z8%NYfR;8QaN8lkNTFhIi$gQb$6ht7W*u&l!Svu3*qG<yosMRv<^#K@ovom16SBumOG>MZ5;Pj^EjWRJTn(x@%6wiNGdTm{Ij;mT8r<d>7AlD6(MSBXuHF5fwmN+TlZGR$e_sz(CXH0R1%1gM<94Qm!L1{s>T>04?&d@K#f7Z9eG19Dx*xtni9+zQe$p2X3T@edv4x;Wok^_s`^lCf|ZD14Y@IB1Se?xTNot^oIWubPSKq{5uyTy<0(iDspxDrjg`AT0boQIPf5Q|5rzJGFV$<KJoT1aRJqUO$S+Bc=Ed^E2~S*4ZLQFBg;T>(Qz;=z#9mf&8=k`;lTaENL-exV_;OW#{?ng7SuF_GS9~c;iX@MCqchEFViVX|%p+Uli#dh|v$m<byq(wx*LyBK>4e>sP9mebVi`pWyPD*E*Rd<4bgeEj70@nyO_`8V%ITQ=&@(9>2O-cywrTVm)5)P9RMCzMds2b#*~Q}ZT~5yR+9@RN^2_ptz@9Rv{@y!Tr)VR#N;{@i>YG6`ZnhT0!<EYgon<@NUZRR667Zri<8@u@wiLHM|Jn|lPTVL=TLQk*$j;8*UVXv}Zi9RZ_Gx;u8xXQT)Db!qy`?Km33d9Oy0<lV1q$<(8O&R$fs!5{Ohu87>Ny9l=m0fS|9D<wY)K$u(uRI!1#;mSuHjU-J>bVtj~FDCP&14<X^ZsbTl%P$Zz!30R$+Oh=;KX#r?;_r@qCS#o`9Cwc?D_kK)2z6GJx7>om6+REE0iME9zLS>M>S^-IXd1T1tht8N?@J%Vkf6FldKg?-SJI|Hjp7Z^ow;`O$qoGzc)gXgLz4KJRZKfTU&8OtPzb`ZjB9CAFmN_1r0|yWcC<W`N8)FbKvaH6-gJ=T{|@;I!AmeLZ6v@(n}aZ_Sy?lr^4o()!WRiA)^1@Z@R8Ov?5wO@asiueTDl7bs-KF~r?GA~-3JhTPiO`X#E7&Om7sSuEV(P{rd*TMa1`bqZAmU8Obde!Z0zdJ7Rlz2l`F57A}RC2w}LL))XPtL^6g&HZ+{X%uxmddLEo&F{VUWF3x)l+16Im?q+ol9ZUTbF*BsPRpJ>J0C&l;Yef~LtAV2(&2^%@^G#M-@T*D%XjBvpiqA3o~Z~+cd0-0qzcXC+PI8;7WrKki{BdgU0m6CvzF~r6*J1dd9UNuyVg>-8@zB?@MYDxjSovjQhx(Drv}K~Q|xFccss9<?Z#~MDxStVC*veu-h~`|JMnD49i7)LD{Eu9RoGd%WH2*~eM8<mdb(o!iT8|bma50qS_dhyjBRRzItn~eW#ib5f}J95?DnG`sdf9NL&Q^Zc>p~#*SP7HnoA=glrYcUi&vEiwd}E9KvC^qd-p;#LXw;8hDr@q*JrMvK*vbnWor@HV`3Fpd7KHj0Fdd6tt0->WAkKuTYHNauduPRFo~a~VJ+;yv?y8aQHcgkZx1EBL<8q)B=+HhA2PbPBS-nTOv*qXPG|U})@U`|dESLj2!zV2?tj;@*LBYBChD^o@O}bHOcSThp~mX_a9EoNYhk)P{$-)S3E^eeEa9P+R}lWn^XD7s)qI402bq$**X{9Jw43O;?%~kIg2p9VO*B+rQpnRliso!dim$NtITAEqUu!pq1`%0?OvJEH4I1~P{bSL(Dg~B(ARB@O2NbMUfH{hal3<dq4u`$S2KIzAM%WSx^fC&U)@E{}@@TxT0j(w%-Eyx%tD8f^?HNoG$$#hY*zgtA?PfX!{uAcFzvt{%<CobpH8O_Os{b5f&A+UTm&p5liO@jb+sd<`4*cKS{LSK($Su5|iNtBCFNy1JA>%AB#iqe8te`k_b&xE0rc&FZTI%6W?ASrI`DCl4h!;Y^+d~-u=sI=(678tOBn<`w3{^!*#1X2ED*c8rQ90}J!SJx{;{|oO5iFq!o3cueVLZtk0Wcwvim^Ky8X_hptt-Ro#Y*jHG8=ZUz6cwUl}=+h`A+ePPsXS!q>L}PmssP**sokMI<?;?{bKJWo6KnP#KlHbvsbJ4oQ&0FpQE2Y{ZvsO%lB*Ja>ZLa52k#SO8sO6zITmIyoHL-LAG(kts;MSR2~7VLp%^!O?-#4SB-kX>M?jFn0{%mx>|qur(-K3XtepZ7H6`Po~MJ$8s|BK+E(I&lXY*wPS$rWP8GvPTqG1V#$`qu42SPjjcbpi!d)i$|8ew<c6CpGjL+sQd2v{shvk*%!~*K~_q&-x%O|IK)?|i#>ETjyR@FzTST7aPZu5(H#)O0N=C^n8`Jd^Du0QcQhfH@?Sbem3KR_dsi+}#>@yAbpd%;%QtyI7J+Yf*J?n^ZA>GWLuzWV3C|K)i6$;yP!RQ}&SsXD%{e;K!Mry=3_W1ohdE#^P{`ooXk|MT-3{pHuVIP|L&{EIJ@f~VQP8qVg^qe>%boclWFGcsCF&O3L&s=d$U*H~SBiw!jxRnDLl)3}*)kJ!;46ujHO#(jNhd8O~|-k{)@oktkwZ`aWXyO{8LWE0cPv~B+C%|_>`hYiQ9#wftKh3qc(UCi+&4)4jLQoxI<QPRL~xY)xZM}P5xj~z-*FLr6oSp02Y2{WC#HMTs#sD1;veBK0^#Zhmx3mN^{D&a3HkbQlsg?f=F<m66kyL^6HsCy${dEY55jga58wzM5Y5BL$GQjVd_MDio+E0DFv5Mi6izJX6d9-lOGOc{ZEi7v9Q+?INcoIJZ{Z)X*^*wVK2^6|!Vml4FrHWn64=MC;q2PFbHv2u^{gUMEEaN0${YSY+vc6O$nL3YDfmOk#d=l!<x;QrWCw{K|hpJ{NrkZ^X4Nv?G1-eKs1aMu9e{iH*S-*cAiM6GzGY)9`q)r<lpPj}NvCdqnomP3+r{VZ$qs{tu-vXx0W=AknWbW3TrhX?M;Y}Q<(9%lzB+%xa2MwiXj%$5zWm)EKyDx~`Mq2JVO*@~z+^@9OwgJJS4>n}HHbNMHXzL4_`UO!rYPMqk}2NLvJBQRH0ilV6kBzWbzul>lrTIg{*2Sl2&Mhh_MG`g=tn4SVT4L(}oP2&c#gBpj*vA%(3afx>=d+q7#iN|60Tt6l%B%`zG@N#htoredn;q9^LAM3gx8Fzhn?Y92aIHX;vjVI<CMQ%o)sHyZlezZU}W<kqs)%7q{ewDGytr@%6hVYKszxVhZA~n>4OrBN_u**RA8hvRN8H8AA%e(Qvpn5~+PkJRsJ5c%{(wcm(Swg#_xNM$im)<?o$m{x_U)b2UUmyK>i=Zfty>^k3Vlx}{Jr@&yWqVssK6A}Sa9MtS%#7XaTQm1h8G1&7^T`l?LrvAJ>ZvLB4aCI7jzk*_EV>Q--Sa-96JjH+c(29a2w*A|HYVfBjX8ot0lUTaPbo;G(->@@_eFx{rQ6#3yuDu4+G7ZE0DRuU{KFTWqoxM%BSQK6IjqFkqj<P?>D74q_`4!r_j?xGV)S)4$GtH4t2d`|``<U9qh|0eWbK_FC)wxjA~-g%)gFCMHza9%bn}Jn8272L@@RCis@oAX%&vE`b>5+^LWLUy*W-&F0RQZna!KNpv(qU1DGZkfkYp+0%*~wEi%z)#z|=vQx<m}c@WL%QSs1+<Dkx)A{G2VuWB-ZD-8_2dAm2vIhca?7trJq3Qg3pS0<r$4oM*^^nK%ayjqoeRosDOHBZ4=34lUXW#rW=!plho~Es?y%dzTHg4NtN>xOK;FwVJvu#xE%H`QYnq88vG0E6d+mZ}J?!RFRMEZ?(fA@!<_A_V#b=b~?Yc@~S!V+&vDM7KnJB2hb*r(@FUJ|32S%-+z+}meJYENaF=K8h?nrzcxQiSo3Uyx0MU44MqrWgur$fa!T}1bv+V`i&E&y)iQlcyTrM1WaP{2^__EprL8_jF3l*SiT@(1%ylmrr)L^0z$=!*M)50!-BP!c^GEhn?!;U_^qAU2)p4Iy%A;J&e)-Y6)Sj#89n@c^+A7^x$%hHHRyJ*DE>d#+B{Gf7p9(I~ioDm-?Gt~p)eTi7dl5T8o9l^#oQv6o!r2gTsXxJZQ*o*ctFRhkm?ZvWLPXJ;bFV+|*^f@IR!uW<rafgfjb4>!)2xzr(>B^{*D&xfHf7FN@$+HN#F#LKyOG^33N{HBFD;3lL;0JA_t3?mZ2eQJ{Vsleh473`!N}2NpIXrQ#E%W%(gMLAMTe?s+N+~iVeQozoSmCrMtmxe>$%>QIkpM?tS7Nm`a~HQ(lW=cc2(6SnL8w*B!9Co?AwLIh}8bk<134Sa<=gvT$GrfWg7w;WiF{2s60*I%3)yBeq5LWz?QJuX$`q^C#R!j^6V2D8_tH?%xqTJ^{DV+%Xo7&@+}wfJCZQVRAeP594!8{vFZB8K%;xqdJN2!DCHE%58zmXLKhM{xO*Jb*QVV~Vv3g&;dZmZ5XsPMXjF9~d1JdO(Gn$s7yegzUaTWehhhFTE8^X&O5>dm@Hd|W2TVmjOm^5N-iP+D`v*SgOa#ej`pmulP`+(8{=yq$-UO32>RmAub<KLo$%G>x0X+#Yr$!77*w|@MD1i6tF~2*Ml~$wGO)IY#t4Ve7T^@)#ZFWf@23X#>m%UMJ(NM_BmD?`%8;6+n&6cDTnqVs^&=t>?;vjLTniu(5*X|3o=x_-zotZQ4tE!UZ$fF}7_6#@N`2{rSDo@$&tYfDV=lgg#1~wv~%V1F3&~?5Xv9qbT8OhnF$q_Hsn#UNYc05(RvwWQ*)T3G=0qvM=bvm&ejMBb`DcilHvrV$>W#zT^Jsp=^x=IaJR`N@Ua#bU4+5XbCV{MtPVuVl?Be2}xa0M#uq{>n_B>zkZZ>z$ZYeO_lvs%E?|68OHcgvk`)X=o%4L@xnQwt^&{+6PP>BMPXIj%YZn>YTiX8+bTu2&puEPlpuyyhV>Lmo)>L{+jVd5R$wghkt&U^;Kp(&zZ6KBj7Mda?A*#gC3sy|WU9q{zyNbDCC@3=2S6-3X4vXiGEZ({{^C-EhEI?vlz46h(f63E?%T{{!*uKh!W|S=BC@=XxuY3YiX)dlh%#k*#T3BU$P^fh2aNT`~c!K`aQp1=C$wa^M<;(JagyqbZThEchXfI9)FHDDr4DImMYOBLrCdX-ZaX2BnEiZRh%#7`?*&;`bKZh-iSUKJjfJm+{jUB0R)YubMcVl*w3-4fLF=#Pm(=OlNL#!c~Fh@W?|lN#cy>B&s)&a^Uxm4UPCD8{V_1og~P+B*DA1V5%*8%PN^iDlVv%w<9Wa?=kkx>u=Mj?|zZi?fw*#{Z0ddW&rK}q$nb4-WMFxWbnYnNS8{NTmY9h{5Dr@;SQOLiW+nFyX3x7c+&X=D`5|ZsTyl^$2NS{2r-lvzeZGB$Lf%Ri^BSZt#J#8=ehCpgP3DYhq?HDy|eE4P`=N&<gcGB`Ez2t7M=X^57fV9>flX0PSuU)k2~D?r?*0v#o*N5;70_Ewt^jvN4z<7U~&a&@q2_=B1%xuP{?1f_Y=Zi+5Ovcm^A>nOaH3tiQ}goH8vCvsh)#6PL>Bx3d0+>w)d(wBHTZJ3bxm{)4=&v39$-E4k;feFN@e+PCH(a6Q_m~yS)*xGhoXSAF4@@2b*X58^u!`$AVZVd;o}Gr(_AmL%4)gCzXw??A-a_LfMorDori3ubIv4wfN*jEh>b+!pE6l$Lk5{(eDEm6xsLI^d=J+OH8qS@D_%-eH`@pcEAjRK7<&w-}-fet?1G8)Sqi4h7dL-=1I3&U~qFYus-{^Gs44>u>*zd;SX1uM0J@CTqdZ<rlrLQ0z-<!mnjwBmN9{vFLAnxI+8sVWrd4s{J=gD2e>L+8{={3k(4RAy3c&=qNuX@yNXw0Hg4EN5)THl=vQNtp@Y&k6Tl_$*QhjUb-NH1q`~sfQOlvE*xql|vO`h_dwfi%S!5gKQmMVKifxcu{0x!n(mol<+NC>Hu1nvEUnBC5@?fF{Y@)6^YWYP5(%fA{j35&KTph~pvkXLik$hC+g+E=KY&g>z*$BzExh>(!Nkdw9OTj?e6q8*urlQm~v4vw{e&nkK)@r##4KvfOm3k+3J13#)YF5udZa_`Uh^LWD=4f_-0^7dGggBLbuVg*SdHZOXm-@OFOM~u<hNro=GR4^Fwy5^x<~6k3_o(wDPNo2m+IPcNY0@;vcW|DjKBV!g+XR@8Ux5H)SvcG`zyZ)uxZ0|lyIzHaB#4%_V^C}_h`-0Qpgs_3kiN0J<?V35d0pu4e%ExK-~O>pvtdQ@hJfBN|02_J6k;^!`En`8)wJDPhmzPXwT_c}++JG^<}pwJ+FcZ?g@tdb;_UcBN`;=qV+U(JMx`_U3(^E!EG&-C;CC_fvetjxUUYUmj(Qr`ztFMrtwxNTePEt9IvSlEflR!M_QF7jXKcS%A$qiw_kOb~ERxMo0)3o}T547JoOX<MOyN7T2MD5|j%SCHp4A5QK<+lN4o!7*g$9m%8SP~x>Nv;>F|M3QAt=VsSkrl}dEnI^M@q7Ym?G9S`rXRzJIfu`y2ifO74(l^IT2h`3iQkAgC-Rg?-KIC`Y<q?d5J3*{YO%=^}Y>H#c_o8EoRg|EQBivy$s-78tU4;l9v%nI$s{*4dw2H@M|wOKm~_Lzwb{3V7aETnX34ybWjb^hRKbNRMX6wmRgFxR1*Dtj7YWQMlc6j_SBsuwd3mnQ8;mD8h}Ne#JZk#Ubb3Eo^pn9%jZr(rQ)Wbz}^V9TaIH?=tS{#Tz`$JDSL(Zz1-uW?IUE3nTzX<9W!U0(2sq`0$62$F3VetEXK-n4we?WozSHf%WrSL#?Z(_(O`0dwxJ$?giQq(WlUgKsA(dX@=QE5DIJYJOy;jJ&zYs4M)LcTXk`X}U%&b&0$zz_rIhXasuiHGrxr>0M=(ccOgJXf(WV{K2IMgp3TKS5-c7sm6vS_FGG)UQO3yEYyWRZHQ1F5WyX^o4tqg>M?<l?7y6~?RWx)1N3;Xifj4%nPYmzxVPff35rY7WFlzJbM1Xqv=gV1JE-hD92Gt>j?Vn8tYCwI}P|KAyX6P;+R;p2*<T(%I@&PT^_g~f{pj7xP~grh`8Xfnuj307qT|1xnoZ8EXC{u;}zVZuO7Z-ukfjtj496yT{MT3yrZl}C2#B{f2BttHnIN^(TH=I4_sT(*qDV)mmM9VS7$xy(kGHSL8QR@-Iir8a++UwfKm4ygy^uwFEA^I@`Ck8{uo<5IK$;~LEI+MmbF9`*P+TDID6+qQ;ptVlA>Tw?nUwbtg)8^`Y+!r@j&x0}4n_r`G0F8rppDo?*x-EvuCexSJcCVyTtBPUUoc%ool2e_p)uYyu#2|Kj100GXu9%<%_EbO<|3YQYrCD$V)1e@fY&HA}@VUJ#h>!bSOxYn!X`jHRa2R#ha-^=GV9tWG<ibp8Kar_8CwO5Ss7{qd}RcwQrQGWN>O;TFhL5&oGmWdm@4;%Q)TL3EG|L`vbYq$fAKxdB&h^w`%tx(RBY4@#pksScZs@KO&SCgGmo|_55VkW^V^i<tB^|@XQ)k>DvR!3SqEZpiBWney@V0kE?O_l-7f<w0Nc?V{Dl2V!XkE1k8Y%{MiGm(<{*%fjP5S#!Ady2W?iPH9^lH2X_A4Ny6HTw%hqp6=`(Kyc1Bj+%L4hucnm34o??(yqU#4;3P<!HtW1D<M9?;od3c)wgylri}5s>N7_lcB{;_r)vpasAuscLy;(G(ta_Mgj+*fovq;fPB-J{&gRg!3%g^HK_CnFuRcYQfv)uHo*I~rMMM>Ngr4TTlMX!-Q_+L$vJhZ&&8j4VWkJN_{8Q3i>tytXi}>zx#&!QO&pjcWVJFFw;~Y3u}JzCKV0S^zUW{3cSGP^>C;Go;wXEkW-twSsZnTaLsf7^f9TpxXqW+O=M`FU!hmv&DPWQl`!{Y|(uyd`pk$YK<XyAJUj!Ql)E5Bc2G*X990*wm9q`qHRg=J3&ah0wL^-kQwUQyrCYGJ_*g6@<AFXOj(Syr*mfR&cj@?(62oPB-#+GX~G+pWgposi57()j4#_DVYC8J97z^H_wu(~|sHb(qNee?99mSBMr(#`Nj(`$wdpvLMLz@Xowfs%IMC!1E;5s9J2CaSEC262l$lea|S=i>SumfpKpGh)q1`zYFt<<#Fx!n5Ppa{S7G#>XMsKCVpF+%l1UOtko$3@+=;vC?MIqJ|VA59;N7TEJqdw8k3@(HDPg#H%34q@cV)WaK*X9Ud11<6c0+myH+h8_fnf7>kdbF!tT3@6dx}MJ{%fljW7{=OTQ!`<B(xZUv^17Z%l?$ZTx{v-yq5<1Ux;-EmoC0O0BJYZ_!qGXFODzo2ehFN1;OTB{Bfs2}gVKHtQX)7hyX*_kFEQ)dk--l}7PC<&Rx=pHUIh1JOA+~|X&TKFBuh(k9tB~22ige{W>XT#n$Xl~|m6!2I<Zu4uwaA2Quz$hc%L_}$cPcz`BGf4s*C359SZ-7;8S*+SPzr7@P(FHc7kC*7dLq$ZO_+4l4yo;{CyuqatCnw4xHC<M88Z>v3goeKLT`Kq|s!oyplZJ%8ohw12zkjr+P&Pbv&1!G|cZ4R+?4#;w&%X%9`pE_0`vrattA^<5qN*6j5`-vhtR?hn!W7Zs-~zZP02<B2xa)M>^3Lw<v)s*r0~3qJj27=f5WR>Ut3GOLNwC1W04^g&<Q0!ZFkobsx6Ad8rbn5uyyBY99Ol_8N(7G624=F^T#N?SVr9t)sr4-cLz2UiZLxRGVA&N;y^KOhSFLM4iw~X{=V3VWoSvwD<CX2;6*Xc&;i-IduD_x14{Y#OIx;$*Tn5IZjf5>*ljmk{%42|FSq*^xqqW>M<Xz8s^oY|dkWy-5LlYA_-I(i6a;R_1*ScN%6br^812Qx8goG46E}f`_ESeX44H9@jELtCnly_KfxW1<-wNf%^n3E&pbVMz6!jMxZwB?V$5W{l}9`3++WLU(a7!_|J0I%mtu_3jMrUABd=I<Xk7({Bla7uarAL)+sauEO*1^|a%nCqt=`AoIy)p9xARi|S_G@<cIw*~iRDCGu<zznaaaWiF1br$_Rz6LB~*m+RCYztjFM28lu<Y7N>hCDt>0c25A0}N(#6XVVj@N#NQqAF{pYvdFyLIElkCwrBO$-ont>PTvgkHQTI9g#s11e0Y)WoyUvOjypCGxeSNvC30so0=&>o^N%r*mX1IKFPpRvRM(W40h6>t4f+?wf)qvW+5=6g|ops($=7<8f}r*UkTW3)HhbUGhosY49@EJ$zoT_SQTgrc+My2)tFFI&M%i|g;^`d!K3dpnA#MMu|0o@NLa3brF_`BS|*ms3s$3}IT?gBqb1?fB*0U(k~kcV6|gx#99u=PFgtd?z8ctbF<P+*QV_Uy*g86fDs?TV);&4q;L#F1XdodM(8rPIFg=w@M*9fTI<kfjoM|sUK~lLU-566Qk!{gI9f}6Gk{c2r`w09zY=6{zW_&axQgG6+ZP$mCCcn_xQ*RnXf*RdV{*Y`MihDCir^Ia-EjaXno5Q0mjcUL&7L&+$1d98eep3?WYE=r6dTUxa!olq8geq`8tDwYiuIk)SoyUX0mqK*k3_PiD>YUQXp7u1lF{!4mRbI`|GIbRR-6QVRoHOAT2nmkr+9qcYa;QrVs9q59MF*jJaXK}9Z?igMv8xlSA;aZT@2*t<iwb$ep2}(Iml6bIAyojz#rNz{TaVX4RfCULm+MRH6LJ(lpNNL4syYEW$98{4$3tW$#hJPd)y~8p1>tyHJkOT7-0PgV@olnVbyMNXP16F>TX(D#;)2J{A}Fu&yF{lpoa2RGvRsaif~8i+F9ei>Da%POY}%3q8R!}^m$NuDvQw>^&dX~Zbdy#zIdKsxB5rw&?7(YjEp2Q7=lIMSu{s5s3(MSL){IgL)XtP_*#YH7n+Im*q0k%G6{1Nsh~K=HJzBm7WK(;z+|@l-O#CGWJ)ETU*|_K1F|+2Tb55ekA>c6ZFaABnP8TAJGkYvzuI&#G9JGxnw&54j9l4_$>o~f!2{UZPmOsP*g|QZICOZL^d+Pd2S?3yx(O&KlJgUC&V7Jof;A7B(I@_Q@>U8d6%kOXZZQ=d|(b=h1Sq%mKA_0@ptdpGbwjaVkaf!=-PX&{nfB%|2blcO!sYEvTD3c7&H#tJzhYz)1rhtz;nM8fkTtY9`qjFYNoa>tTTs34y_p;(XsNWEKS14SaZJXRyCgV_ycuigoIB=F~MLEzRImwF~>|ta{&kRs`n*E+2=qW_-j&IR&6_#DPN4}JoBb7zv+Yf~)5@|;~*T}SnP$$|3FCtcW<A|}l6ul{N^|lx|RXta9#U&bc(#I^kDlZ-`NAI*nbKCl|2@|xh-!8iz1FF-ISRg4iWXE&<KaB@X?l|MJW(Y&?8|A*e-^}K6XI~xmoUmy#gY+BeK2Rsc<C%P88`=q?^nha0w!El<e2lmkaO=F9R7p~Com9<>H>qk17-Iu*%5*T$#=^hBdVJUC%oHXD6CF31A7KY=N};+BdU*5+22}~ut6Uacv%j!x`pi|=@uS?v6_um`Tv^22G3n2AHLRh{vP<V`bFJjCDmH~v<V4k`!OpsQ^b<!?j;L^h9ISPypD+E(%ed*@G*#<X+sC{>+a47k!V&fHvC(Onj9N|%?4LWCyF|E?)lNR?&SQFRQ6Nj{OF3APQ7>~Apr;fcrQB0(k$IDp9df5*EjolA+ny(t%f3PDlsOFtn+jG4lXIprD+hfXkZM3F^UIzUoQAz9IbtAy`4G4e|EwW2{P5V|<fz8NIrxK;-}vk0VKFD*h`F{AAk|0E{o64Ehg4zEso8r6QaIJ1+xWQ8HOJ&8Y0dETj@|$xnl(;xoo_svO}qQkSQsV1ZuF=vpNoX=nKMoqW*YuZPO|{K*=NITo;IygtH&}jEMlCIdtHepHtIN3DCYM&M8Wb-;G_v(KT2;Pgzr=zU{Q+~pxMCsybiZNhxeVvIs0#bN<e7QSox7XSD&XxyzL<7SSuen#$n0S@vO481d<l@%*AL|<X&M943>P63PWF)zItWQZDWTO&m$+!5d+ejlWO1gF<yzGwp})o!p;E%kg*&HEn~a@O+Hb%;8i&arlerfRfuuNI;&jSpw;6Ztq?4x9e!GUygL+1?nvJ0p66iM4ebb(upHgUdHXvUU2yV9fbhKO3@4{>5oucwqLL8_p<tYq4y<q`z2?1+)=-fDVuFqR3(KL-t{y@KypGC7bECPmd0=JJqPW;A!D{csxX2RurgLAz6?u5Ck&^ent7Gs(jiE5GVEW0R@7pry(jnHw)f20YAW=dekJ5Fx*~>5#5y@B2ZY47qTw?Xsw24SnZt+1A9s!XC8kWI@b!rQhXrzzk+c3rtxi0@C)^R3p<4|>xS#r4qKAHx-<QfzIUxHU$8_IrgcusTDkaPObCMOGIk^9KT26+-YdWE&naZDjtb*!xD2x<OS$IT8WO0L-q7?h`5!lEir#;z;&a|P!^=Vp|>gdjn7Op6zsuXA;6yuy_L!)aVh$;8+j)pxaQD9XIXRIVnK^F{QiZ%La&8mw1$2byZJ&*Dl+IB2vGULL}m_*p~iu(TEL)+{h^g{@_|Gg{xqac?z`^GV7xbMX~l5A1@Z5_7{pYm2P4_->lsDT-4OqNawnJ1iGyOF_DIZ)J=Onydh=Zrw&Dfe3j7f~Ru{`jW0{j1lq>R4D<}806cLH}s-1%5<zL!JHvA<~C!-JZQY<=KWWu#?-B<549$^+1$xMZVVd12^#+vM#%!FPfUhWbf-^*sDR;k3Q|KVI-5;n<*rWv7}3R3((hA5p}*cs_1Y*;z2z2F?lU>^OVXoxvHWnt6W7xz9AK|-YB*{tB}9qX%W7`Ja~Nb2N+V;4Ue+65uFB7U`tv8N1;P4?FJ(!Q<PmRlrddsF0y~R&WNUme$M9g*Hg%V`6C2@r&!s1wu$$6JWOP?7qex*_lf3Ubc7>F#)kUTP+NG~46H-b!9g`n=CdK0*1bWCejecV~IrM`n+L2*TD)2qKSiHW=$+=!Tg~VNcS-ue1Q|8p)dnfA@ZNye-$Fxd)Gib)m)`EDra=D<hYzNy*RIx+?UNmOBu4~<TG`-u$9X6e~QJA&_e5a9}oxQ#KgcaNd`4sHa^kg?6WPhk5bSQdDSC|s&^gVTNYwijZ<|{Lpw^9QoJwBL<A|2Ip4qVXzYNr12yvEp)K*XdC{mcsF!ZBRKscw6~kE0$jNGhRb7<1AV>C3nDQ7zw4GV`p$@<`FgoAgd^WAozq8ZkWqEwl3q(%^w^@n0CO%t`S*GvQ$?>R7GnJ^!$~QpG__sqi*~_+)Ik?5Pk2?eOb;f|~r_xLWPa7~Nd)`OqN1^rGcRl={5Cg#eP4Ni)f=>gn68v6a-4ve$E`tnPlVT$=$h@1{#?NY+QruSzDtX|IL*dd4>78-~E&nlqItYdq<s^`oH^nK*K_&@qsil<irX1P}gSZzXCkP{@j7h`V`2a8e!(xwW(POH?DBfzl?jSh&HVipQ6>8d50g6siomN^9KxdMhpT79xgv$4fgNqRXgD-t1_Hwnx{@-TOE9+vTQF)b;2g3tTq8_ui9rI3`juzgc3Mh(k(JV#?0Va>+U^d-m*n1fho`k!=iZt=&t98yd*Nxe|Q$jxI0XosWS+`JsEJA}rmd{?L;uG?Q!NGWJ>IcUdfcYvgxvW#i3Swo6saDEsEUj#uwmOWkhp!ezmiRp&N7EEP%p4d9#_Aa_r(qoLsKyh64cv(c+~8ta^llX!U-a`5fMv;B5-Ubn2QjpbHhXXTQ?%rN#1dGF}yitQ)fGqPE#9#?A}q{K3|sSWBV@JN-7V>b$RinOuYk9wrm?VAn}Ps!y0^vqo2rdw(*jf7CbJbN!*RVLK3$9@4twSVp13(*KkZn7IHHCSDrxq<>6BY~H#MP!eORbb_DCg1`<rZ2XR_(PM;lkjcrEnd9B#?HbdewK!{umjVgWVJ^n8Z^B<l<*P_{Pl+)|Mg35j(zyxhm7v+$WcBnlQPhU(-}UgHCjz~o_FCB0->_1``>l!b)B=jiTW%Cyq|y))5NKBsImG!9M&enT9_`6e_1GSLU`FVOL(Z|6@<U?{P{+DH6NkhL8c_{b$k34?IwDzdpLBlpmE7o6Ajgu6!J8XqB&cV;w!9ujs(ru*V@gYK}41z6EW;lgT_5+|5&uHN`Yk`$VN%l0R^iSV2+}qB$%YD!(lJ7fj!}j5w?T^y^O-8wVB+gJR0w7K&#0`x7=&c>gLdJdj^w4s^T3U8@{5t-At#zf5II2_niG|{4#r{M#hj@^`Aqm`Ioiv5_!Kb5gO=wTX`1Lf&Y7(zgfHzxrO&LkvJ{&C2`#?WSr%t*fjWs6%>cA4w41WRBC%vOFi6)9XqHtpKO^F@k}Uqdnf|{U8n9}q8*i(q`_c-p{gi}I6}2irQa|nDrY@D7#_BLyr3>Of+bX8Q&#CQj3=2R045|-F?L5oL&U_Sb!Aw+Sg9RNX2b5)7hxl^(rGLw-zh%v$rx3Il<@`k5^LNT`;{w3r}q1#U+lePlNn8(xY&ql_G<N>ld-z&bM*74pDOBOtzCC<x#F#z2U9*urG7F3-@8U9-a^IaAlo?NR*}CuDvyBGAs&dVCcZ=2t46(G^%%SoOuw{OU9CU-)3Fs1G}?Syi!<3t&(pzWjq{vAZ7cD?$-1{-C+j;Gr;6btE)t3w<1(WShQoKN#<j;$;VzT>|2X<aySk@8#%FVuyg01R!}3aWVgdF0``yf;<&)DqYcj*W^l+&;tLmdvte1*txB121L3#7ryLfzj{Qm(8`kSK')).decode("utf-8"))
_ITEMS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG",
    "MILK", "WOOL", "FERTILIZER", "GOOSE", "COW", "SHEEP",
)
_PRODUCTS = _ITEMS[:9]
_CROPS = _ITEMS[:5]
_SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
_LAND_COST = (1000, 2000, 4000)
_SEGMENT_TURNS = 72
_HERD_DECISION_STEP = 145
_YARN_CONVERT_THRESHOLD = 1
_WOOL_GATE = 60
_SWEEP_STEPS = (707, 712, 716, 718)
_SWEEP_ITEMS = ('WOOL', 'MILK', 'WHEAT', 'FERTILIZER')
_FEEDCUT_STEP = 456
_FEEDCUT_WOOL = 12
_FEEDCUT_MILK = 15
_SHEEP_YIELD = 33
_COW_YIELD = 36
_RATIO = 0.6
_MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")
_DECISION_STEP = 360
_TURNS = 719
_STATE = {
    0: {"last_step": -1, "route": 0, "herd": 0},
    1: {"last_step": -1, "route": 0, "herd": 0},
}


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _seat(observation):
    return 1 if int(_get(observation, "player", 0) or 0) == 1 else 0


def _farm(observation, seat):
    farms = list(_get(observation, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _plant_tiles(farm):
    result = 0
    for row in (_get(farm, "tiles", []) or []):
        for tile in row or []:
            if isinstance(tile, str):
                result += tile == "PLANT"
            elif tile is not None:
                result += _get(tile, "kind") == "PLANT" or bool(_get(tile, "crop"))
    return result


def _select_route(observation, seat):
    town = _get(observation, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    if not shops:
        return 0
    market = _get(observation, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    if shops[0] == "BAKERY" and float(_get(inventory, "FERTILIZER", 0) or 0) <= 10232.5:
        return 1
    if shops[0] == "PET_CAFE":
        rival = _farm(observation, 1 - seat)
        if float(_plant_tiles(rival)) <= 64.5:
            return 1
    return 0


def _quantity(order):
    try:
        return max(1, int(order[2])) if len(order) >= 3 else 1
    except (TypeError, ValueError):
        return 1


def _fib(index):
    previous, current = 1, 1
    for _ in range(max(0, int(index))):
        previous, current = current, previous + current
    return previous


def _existing_sale(action, item):
    return sum(
        max(0, int(order[2]))
        for order in (action.get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


def _owned_in_hands(observation, item):
    private = _get(observation, "private", {}) or {}
    inventories = list(_get(private, "inventories", []) or [])
    farm = _farm(observation, _seat(observation))
    n_units = 1 + len(_get(farm, "hands", []) or [])
    total = 0
    for carried in inventories[:min(n_units, 40)]:
        total += max(0, int(_get(carried or {}, item, 0) or 0))
    return total


def _requirements(observation, route, herd, start, end):
    market = _get(observation, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    farm = _farm(observation, _seat(observation))
    quadrants = len(_get(farm, "unlocked_quadrants", []) or [])
    balances = {item: 0 for item in _ITEMS}
    starting = {item: 0 for item in _ITEMS}
    hires_by_day = [0] * 6
    purchase_budget = 0.0

    for step in range(start, end):
        action = _ROUTES[route][herd][step]
        units = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
        for operation in units:
            if not operation:
                continue
            if operation[0] == "FEED":
                balances["WHEAT"] -= 1
                starting["WHEAT"] = max(starting["WHEAT"], -balances["WHEAT"])
            elif operation[0] == "FERTILIZE":
                balances["FERTILIZER"] -= 1
                starting["FERTILIZER"] = max(starting["FERTILIZER"], -balances["FERTILIZER"])
            elif operation[0] == "PLACE" and len(operation) >= 2 and operation[1] in balances:
                item = operation[1]
                balances[item] -= _quantity(operation)
                starting[item] = max(starting[item], -balances[item])

        for order in action.get("market") or []:
            if not order:
                continue
            kind = order[0]
            item = order[1] if len(order) >= 2 else ""
            quantity = _quantity(order)
            if kind == "HIRE":
                day = min(5, max(0, (step - start) // 24))
                hires_by_day[day] += 1
            elif kind == "BUY_LAND":
                extra = quadrants - 1
                if 0 <= extra < 3:
                    purchase_budget += _LAND_COST[extra]
                    quadrants += 1
            elif kind == "BUY_SEED" and item in _SEED_COST:
                purchase_budget += _SEED_COST[item] * quantity
            elif kind == "BUY_PRODUCT" and item in {"WHEAT", "FERTILIZER"}:
                purchase_budget += float(_get(prices, item, 0) or 0) * quantity
                balances[item] += quantity
            elif kind == "BUY_ANIMAL" and item in _ANIMAL_COST:
                purchase_budget += _ANIMAL_COST[item] * quantity
                balances[item] += quantity

    first_hire = max(0, int(_get(farm, "hires_today", 0) or 0))
    for day, count in enumerate(hires_by_day):
        offset = first_hire if day == 0 else 0
        for index in range(count):
            purchase_budget += _fib(offset + index)
    return purchase_budget, starting


def _add_budget_sale(action, item, quantity, max_orders):
    if quantity <= 0:
        return True
    for order in action["market"]:
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item:
            order[2] = max(0, int(order[2])) + quantity
            return True
    if len(action["market"]) >= max_orders:
        return False
    action["market"].append(["SELL", item, quantity])
    return True


def _budget_guard(action, observation, route, herd, step):
    if step % _SEGMENT_TURNS != 0:
        return action
    end = min(_TURNS, step + _SEGMENT_TURNS)
    purchase_budget, starting = _requirements(observation, route, herd, step, end)
    private = _get(observation, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    market = _get(observation, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    farm = _farm(observation, _seat(observation))
    available_cash = float(_get(farm, "money", 0) or 0)
    for item in _PRODUCTS:
        sold = min(max(0, int(_get(shed, item, 0) or 0)), _existing_sale(action, item))
        available_cash += sold * float(_get(prices, item, 0) or 0)
    shortfall = purchase_budget - available_cash
    if shortfall <= 0:
        return action

    candidates = []
    for order_index, item in enumerate(_PRODUCTS):
        price = int(_get(prices, item, 0) or 0)
        if price < 2:
            continue
        protected_shed = max(0, starting[item] - _owned_in_hands(observation, item))
        available = max(
            0,
            int(_get(shed, item, 0) or 0) - protected_shed - _existing_sale(action, item),
        )
        if available > 0:
            candidates.append((item, available, price, order_index))
    candidates.sort(key=lambda candidate: (-candidate[2], candidate[3]))

    result = _copy_action(action)
    added = False
    for item, available, price, _ in candidates:
        if shortfall <= 0:
            break
        needed = int(math.ceil(shortfall / price))
        quantity = min(available, needed)
        if _add_budget_sale(result, item, quantity, 10):
            shortfall -= quantity * price
            added = True
    if added:
        sales = [order for order in result["market"] if order and order[0] == "SELL"]
        others = [order for order in result["market"] if not order or order[0] != "SELL"]
        result["market"] = sales + others
    return result




def _shop_counts(observation):
    town = _get(observation, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    yarn = sum(1 for name in shops if name == "YARN_STORE")
    milk = sum(1 for name in shops if name in _MILK_SHOPS)
    return yarn, milk


def _prices(observation):
    market = _get(observation, "market", {}) or {}
    return _get(market, "prices", {}) or {}


def _shed(observation, seat):
    priv = _get(observation, "private", {}) or {}
    return _get(priv, "shed", {}) or {}


def _scheduled_after(route, herd, step, item):
    total = 0
    tape = _ROUTES[route][herd]
    for s in range(step + 1, len(tape)):
        for order in tape[s].get("market") or []:
            if len(order) >= 3 and order[0] == "SELL" and order[1] == item:
                total += int(order[2])
    return total


def _epoch_convert(observation, seat):
    """v29 trigger (rule=milk0): convert whenever no milk shop seen by 145.

    Rationale: shops drawn with replacement from an 8-type pool (1 yarn);
    yarn is seen by step 145 in only ~14% of games but unlocks eventually in
    ~57% (live 108-game study) — late yarn is uncatchable after the pipeline.
    No-milk-shop + no-yarn-ever games are ~neutral (dead wool px 2-3 vs dead
    milk px 1). Species-agnostic conversion.
    """
    _yarn, milk = _shop_counts(observation)
    yarn, _milk = _shop_counts(observation)
    return 1 if (yarn >= _YARN_CONVERT_THRESHOLD and _milk == 0) else 0



def _sweep(action, observation, seat, route, herd, step):
    if True:
        return action
    shed = _shed(observation, seat)
    if not shed:
        return action
    orders = list(action.get("market") or [])
    for item in _SWEEP_ITEMS:
        have = int(shed.get(item, 0) or 0)
        if have <= 0:
            continue
        surplus = have - _scheduled_after(route, herd, step, item)
        if surplus <= 0:
            continue
        if len(orders) >= 10:
            break
        orders.append(["SELL", item, surplus])
    if len(orders) != len(action.get("market") or []):
        action["market"] = orders
    return action


def _feedcut(action, observation):
    return action
    prices = _prices(observation)
    if (float(_get(prices, "WOOL", 0) or 0) >= _FEEDCUT_WOOL
            or float(_get(prices, "MILK", 0) or 0) >= _FEEDCUT_MILK):
        return action
    for key in ("farmer", "hands"):
        ops = action.get(key)
        if not ops:
            continue
        if key == "farmer":
            if ops[0] in ("FEED", "CARE"):
                ops[0] = "PASS"
        else:
            for op in ops:
                if op and op[0] in ("FEED", "CARE"):
                    op[0] = "PASS"
    return action


def _wool_gate(action, observation, herd):
    if herd != 1:
        return action
    prices = _prices(observation)
    if float(_get(prices, "WOOL", 0) or 0) >= _WOOL_GATE:
        return action
    kept = [order for order in action.get("market") or []
            if not (isinstance(order, list) and len(order) >= 3
                    and order[0] == "SELL" and order[1] == "WOOL")]
    if len(kept) != len(action.get("market") or []):
        action["market"] = kept
    return action


def agent(observation, configuration=None):
    del configuration
    try:
        seat = _seat(observation)
        step = int(_get(observation, "step", 0) or 0)
        state = _STATE[seat]
        if step == 0 or step < int(state.get("last_step", -1)):
            state = {"last_step": -1, "route": 0, "herd": 0}
            _STATE[seat] = state
        if not 0 <= step < _TURNS:
            farm = _farm(observation, seat)
            return {
                "farmer": ["PASS"],
                "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
                "market": [],
            }
        if step == _HERD_DECISION_STEP:
            state["herd"] = _epoch_convert(observation, seat)
        if step == _DECISION_STEP:
            state["route"] = _select_route(observation, seat)
        route = int(state.get("route", 0))
        herd = int(state.get("herd", 0))
        action = _copy_action(_ROUTES[route][herd][step])
        action = _budget_guard(action, observation, route, herd, step)
        action = _wool_gate(action, observation, herd)
        action = _sweep(action, observation, seat, route, herd, step)
        action = _feedcut(action, observation)
        state["last_step"] = step
        return action
    except Exception:
        farm = _farm(observation, _seat(observation))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }
